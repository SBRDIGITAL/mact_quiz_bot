from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import StatesGroup, State

from core.logging.my_logger import MyLogger



# Определяем состояния
class QuizFormStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


class QuizRouter:

    def __init__(self) -> None:
        self.logger = MyLogger(name='QuizRouter_logger', is_console=False).get_logger()

    async def start_quiz(self, call: CallbackQuery, state: FSMContext) -> None:
        await call.message.answer('Я работаю!')

