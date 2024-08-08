import traceback

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from core.logging.my_logger import MyLogger
from core.config.config_reader import config



logger = MyLogger(name='main_py_logger').get_logger()



class StartBot:
    def __init__(self) -> None:
        self.bot = Bot(  # Экземпляр бота
            token=config.bot_token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()  # Диспетчер
        self.db = DataBase()  # БД
        self._include_middlewares()  # Прокидываем мидлвари в диспетчер
        self._include_routers()  # Подключаем роутеры
        self._start()  # Запускаем бота

    def _include_middlewares(self) -> None:
        self.dp.callback_query.middleware(  # Автоответ телеграму об обработке колбэков
            CallbackAnswerMiddleware()  
        )

    def _include_routers(self) -> None:
        """  ## Подключение роутеров """

        self.dp.include_routers(
            add_realty.router,  # Обработчик добавления объекта недвижимости в БД
        )

    async def __main(self) -> None:
        """  ## Запуск процесса полинга """
        await self.bot.delete_webhook(drop_pending_updates=True)  # Пропуск обновлений
        await self.dp.start_polling(  # Запуск пуллинга
                self.bot,
                db=self.db
            )

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