import json

from os.path import join as join_path, exists as file_exists, basename
from os import remove

from typing import Dict, List

from asyncio import to_thread

import aiofiles

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext


from core.config.consts import DATA_DIR_PATH
from core.logging.my_logger import MyLogger
from core.states.user_states import QuizFormStates





class QuizRouter:

    def __init__(self, bot: Bot, ADMIN_ID: int) -> None:
        self.ADMIN_ID:int = ADMIN_ID
        self.bot: Bot = bot
        self.logger = MyLogger(name='QuizRouter_logger', is_console=False).get_logger()
        self.questions_json_path:str = join_path(DATA_DIR_PATH, "questions.json")
        self.answers_json_path:str = ''
        self.questions_list:List[str] = []
        self.answ_index = 1
        self.user_answers:Dict[str] = {}
        self.current_qst:str = ''

    async def __read_json_file(self) -> Dict:
        """ ## Читает json файл и возвращает содержимое """
        # Используем aiofiles для асинхронного чтения файла
        async with aiofiles.open(self.questions_json_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
        
    async def __save_json_file(self) -> Dict:
        """ ## Сохраняет в .json файл ответы пользователя """
         # Сначала преобразуем словарь в строку JSON
        json_data = await to_thread(json.dumps, self.user_answers, ensure_ascii=False, indent=4)
        async with aiofiles.open(self.answers_json_path, mode='w', encoding='utf-8') as f:
            await f.write(json_data)

    async def __make_questions_list(self) -> None:
        """ ## Пополняет список вопросов """
        this_questions:Dict = await self.__read_json_file()
        for qst in this_questions['questions'].values():
            self.questions_list.append(qst) if qst not in self.questions_list else None

    def __make_json_answers_file_name(self, telegram_id:int|str) -> None:
        """ ## Создаёт имя файла на основе telegram_id пользователя """
        self.answers_json_path = join_path(DATA_DIR_PATH, f'{telegram_id}_user_answers.json')

    async def start_quiz(self, call: CallbackQuery, state: FSMContext) -> None:
        await to_thread(self.__make_json_answers_file_name, call.from_user.id)
        err_msg:str = 'При старте квиза возникла ошибка'
        try:
            await state.set_state(QuizFormStates.waiting_for_answer)
            await self.__make_questions_list()
            await call.message.answer('Погнали!')
            await call.message.answer(self.questions_list[0])
            self.current_qst = self.questions_list[0]

        except TelegramBadRequest as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)

        except Exception as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)    
    
    def __delete_qst(self) -> None:
        """ ## Удаляет элемент под индексом 0 из списка questions_list """
        try:
            del self.questions_list[0]
        except Exception as ex:
            self.logger.exception(exc_info=ex, 
                msg='При удалении элемента из списка self.questions_list воникла ошибка')    
        
    def __save_user_answer(self, user_answer: str) -> None:
        """ ## Сохраняет ответ пользователя в словарь """
        self.user_answers[f'answer_{self.answ_index}'] = user_answer
    
    async def __delete_file(self) -> None:
        """ ## Удаляет файл с ответами, если он существует """
        if await to_thread(file_exists, self.answers_json_path):
            await to_thread(remove, self.answers_json_path)

    async def __notify_admin_about_new_answ(self) -> None:
        """ ## Отправляет файл администратору """
        if await to_thread(file_exists, self.answers_json_path):
            await self.bot.send_document(self.ADMIN_ID, document=FSInputFile(
                self.answers_json_path, basename(self.answers_json_path)),
                caption='Ответ от нового пользователя!')

    async def handling_user_answer(self, message: Message, state: FSMContext) -> None:
        err_msg:str = f'При получении ответа на вопрос "{self.current_qst}" '+\
            'от пользователя возникла ошибка'
        try:
            await to_thread(self.__save_user_answer, message.text.strip(' ').strip())
            if self.questions_list:  # Если список не пустой
                await message.answer(self.questions_list[0])
                self.current_qst = self.questions_list[0]
                await to_thread(self.__delete_qst)
                self.answ_index += 1
                return
            
            await state.clear()
            await message.answer('Вы ответили на все вопросы!\nСпасибо!')
            await self.__save_json_file()
            await self.__notify_admin_about_new_answ()
            await self.__delete_file()

        except TelegramBadRequest as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)

        except Exception as ex:
            await to_thread(self.logger.exception, msg=err_msg, exc_info=ex)    