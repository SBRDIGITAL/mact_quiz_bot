from dataclasses import dataclass

from os import makedirs

import asyncio
from asyncio import sleep as async_sleep

from typing import List

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import StateFilter

from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from core.config.consts import CORE_DIR_PATH, DATA_DIR_PATH
from core.logging.my_logger import MyLogger
from core.config.config_reader import config

from core.handlers import main_menu
from core.handlers.quiz_router import QuizRouter
from core.states.user_states import QuizFormStates



logger = MyLogger(name='main_py_logger', is_console=False).get_logger()


@dataclass
class StartBot:
    ADMIN_ID:int = int(config.ADMIN_ID.get_secret_value())
    bot = Bot(  # Экземпляр бота
        token=config.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()  # Диспетчер
    
    def __post_init__(self) -> None:
        """ ## Выполняет методы после инициализации """
        self._create_data_dirs()
        self._include_middlewares()  # Прокидываем мидлвари в диспетчер
        self._include_routers()  # Подключаем роутеры
        self._start()  # Запускаем бота

    def _create_data_dirs(self) -> None:
        """ ## Создаёт директории если они не существуют """
        my_dirs:List[str] = [CORE_DIR_PATH, DATA_DIR_PATH]
        [makedirs(this_dir, exist_ok=True) for this_dir in my_dirs]

    def _include_middlewares(self) -> None:
        self.dp.callback_query.middleware(  # Автоответ телеграму об обработке колбэков
            CallbackAnswerMiddleware()  
        )

    def __include_quiz_router(self) -> Router:
        """ ## Подключает роутер квиза """
        router = Router()
        quiz_handler = QuizRouter(self.bot, self.ADMIN_ID)
        router.callback_query.register(
            quiz_handler.start_quiz, F.data.in_(('go_answer_to_questions')))
        router.message.register(quiz_handler.handling_user_answer, 
            StateFilter(QuizFormStates.waiting_for_answer,), F.text)
        return router

    def _include_routers(self) -> None:
        """  ## Подключение роутеров """

        self.dp.include_routers(
            main_menu.router,  # Обработчик добавления объекта недвижимости в БД
            self.__include_quiz_router()
        )

    async def __main(self) -> None:
        """  ## Запуск процесса полинга """
        try:
            await self.bot.delete_webhook(drop_pending_updates=True)  # Пропуск обновлений
            await self.dp.start_polling(  # Запуск пуллинга
                    self.bot,
                    # self.ADMIN_ID
                )
        finally:
            await async_sleep(0.15)
            await self.bot.session.close()

    def _start(self) -> None:
        """  ## Запуск бота """
        asyncio.run(self.__main()) 

    

if __name__ == '__main__':
    try:
        StartBot()
    
    except KeyboardInterrupt:
        print('[INFO] Бот выключен с помощью ctrl + c')

    except Exception as ex:
        logger.error("Конструкция if __name__ == '__main__'", exc_info=ex)