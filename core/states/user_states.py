from aiogram.fsm.state import StatesGroup, State


# Определяем состояния
class QuizFormStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()
