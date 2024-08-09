import json

from os.path import join as join_path, exists as file_exists, basename
from os import remove

from typing import Any, Dict, List

from asyncio import to_thread

import aiofiles

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, FSInputFile, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


from core.config.consts import DATA_DIR_PATH
from core.logging.my_logger import MyLogger
from core.states.user_states import QuizFormStates
from core.utils.keyboards.kb_builder import BotKeyboardsBuilder as BKB



class QuizRouter:

    def __init__(self, bot: Bot, ADMIN_ID: int) -> None:
        self.bkb = BKB()
        self.ADMIN_ID:int = ADMIN_ID
        self.bot: Bot = bot
        self.logger = MyLogger(name='QuizRouter_logger', is_console=False).get_logger()
        self.questions_json_path:str = join_path(DATA_DIR_PATH, "questions.json")
        self.answers_json_path:str = join_path(DATA_DIR_PATH)
        self.questions_list:List[str] = []

    async def __read_json_file(self) -> Dict:
        """ ## Читает json файл и возвращает содержимое """
        # Используем aiofiles для асинхронного чтения файла
        async with aiofiles.open(self.questions_json_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
        
    async def __save_json_file(self, telegram_id: int, save_data: Dict[str, List[str]]) -> str:
        """ ## Сохраняет в .json файл ответы пользователя """
        file_path:str = await to_thread(self.__make_json_answers_file_name, telegram_id)
        save_data['telegram_id'] = telegram_id  # Добавляем telegram_id в save_data
        json_data:str = await to_thread(json.dumps, save_data, ensure_ascii=False, indent=4)
        async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
            await f.write(json_data)

        return file_path

    async def __make_questions_list(self) -> List[str]:
        """ ## Пополняет список вопросов """
        this_questions:Dict = await self.__read_json_file()
        ql:List[str] = []
        for qst in this_questions['questions'].values():
            ql.append(qst) if qst not in ql else None
        
        return ql

    def __make_json_answers_file_name(self, telegram_id:int|str) -> None:
        """ ## Создаёт имя файла на основе telegram_id пользователя """
        self.answers_json_path = join_path(DATA_DIR_PATH, f'_{telegram_id}_user_answers.json')
    
    def __delete_qst(self, qst_list:List[str]) -> List[str]:
        """ ## Удаляет элемент под индексом 0 из списка questions_list """
        try:
            del qst_list[0]
        except Exception as ex:
            self.logger.exception(exc_info=ex, 
                msg='При удалении элемента из списка self.questions_list воникла ошибка')

        return qst_list 
    
    async def __delete_file(self, file_path:str) -> None:
        """ ## Удаляет файл с ответами, если он существует """
        if await to_thread(file_exists, file_path):
            await to_thread(remove, file_path)

    async def __notify_admin_about_new_answ(self, file_path:str) -> None:
        """ ## Отправляет файл администратору """
        if await to_thread(file_exists, self.answers_json_path):
            await self.bot.send_document(self.ADMIN_ID, document=FSInputFile(
                file_path, basename(file_path)),
                caption='Ответ от нового пользователя!')

    async def handling_user_answer(self, message: Message, state: FSMContext) -> None:
        err_msg:str = f'При получении ответа на вопрос от пользователя возникла ошибка'
        
        # Получаем данные состояния
        state_data: Dict[str, Any] = await state.get_data()
        old_questions_list: List[str] = state_data.get('questions_list', [])
        old_user_answers: Dict[str, List[str]] = state_data.get('user_answers', {})
        answer_index: int = state_data.get('answer_index', 0)
        
        try:
            new_qst_list:List[str] = await to_thread(self.__delete_qst, old_questions_list)
            # Сохраняем ответ пользователя
            user_id = message.from_user.id
            if user_id not in old_user_answers:
                old_user_answers[user_id] = []
            old_user_answers[user_id].append(message.text.strip())

            # Обновляем состояние
            await state.update_data(user_answers=old_user_answers)
            await state.update_data(questions_list=new_qst_list) 
                
            if new_qst_list:  # Если список не пустой
                await message.answer(
                    f"{message.from_user.first_name}, {new_qst_list[0].lower()}", 
                    reply_markup=await self.bkb.skeep_qst_btn())
                return
            
           
            await message.answer(
                f'{message.from_user.first_name}, вы ответили на все вопросы!\nСпасибо!',
                reply_markup=ReplyKeyboardRemove())
            
            all_answers:Dict[str, List[str]] = state_data.get('user_answers', {})
            file_path:str = await self.__save_json_file(message.from_user.id, all_answers)
            await self.__notify_admin_about_new_answ(file_path)
            await self.__delete_file(file_path)


            await state.clear()

            # Очищаем содержимое после отправки админу
            self.user_answers.clear()  # Очищаем словарь с ответами
            self.current_qst = ''      # Очищаем текущий вопрос

        except TelegramBadRequest as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)

        except Exception as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)    

    async def start_quiz(self, call: CallbackQuery, state: FSMContext) -> None:
        err_msg:str = 'При старте квиза возникла ошибка'
        try:
            qst_list:List[str] = await self.__make_questions_list()
            await state.set_state(QuizFormStates.waiting_for_answer)
            await state.update_data(user_answers = {})
            await state.update_data(answer_index = 0)
            await call.message.answer('Погнали!')
            await call.message.answer(
                f"{call.from_user.first_name}, {qst_list[0].lower()}",
                reply_markup=await self.bkb.skeep_qst_btn())
            
            new_qst_list:List[str] = await to_thread(self.__delete_qst, qst_list)
            await state.update_data(questions_list = new_qst_list)

        except TelegramBadRequest as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)

        except Exception as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex) 