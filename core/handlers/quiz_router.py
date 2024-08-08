from aiogram import Router
from aiogram.types import CallbackQuery



router = Router()


class QuizRouter:

    async def start_quiz(call: CallbackQuery) -> None:
        pass