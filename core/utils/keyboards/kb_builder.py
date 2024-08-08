from typing import Dict, List

from asyncio import to_thread

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


class BotKeyboardsBuilder:

    def __init__(self) -> None:
        self.BOT_KEYBOARDS:Dict[str, List[List[str]]] = {
            "main_menu_kb": [
                ['Ответить на вопросы', 'go_answer_to_questions']
            ]
        }

    def __get_builder(self) -> InlineKeyboardBuilder:
        """ ## Возвращает объект строителя клавиатур """
        builder = InlineKeyboardBuilder()
        return builder

    async def __inline_builder(self, kb_data: List[List[str]],
        sizes: int = 2, **kwargs) -> InlineKeyboardMarkup:
        """ ## Строитель клавиатур """
        builder = await to_thread(self.__get_builder)
        for kb_btn in kb_data:
            await to_thread(builder.button, text=kb_btn[0], callback_data=kb_btn[1])
        await to_thread(builder.adjust, sizes)

        return await to_thread(builder.as_markup, **kwargs)

    async def main_menu_kb(self, sizes: int = 1) -> InlineKeyboardMarkup:
        """ ## Создаёт клавиатуру главного меню """
        return await self.__inline_builder(self.BOT_KEYBOARDS['main_menu_kb'], sizes)

        

        