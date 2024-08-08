from asyncio import to_thread

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from core.config.consts import TEXT_ANSWERS_TXT
from core.logging.my_logger import MyLogger
from core.utils.state_utils.clear_state import clear_state


logger = MyLogger(name='main_menu_logger', is_console=False).get_logger()
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await clear_state(state)
    try:
        await message.answer(TEXT_ANSWERS_TXT['main_menu_txt'])
    
    except TelegramBadRequest as ex:
        await to_thread(logger.exception,
            msg='При очистке состояния произошла ошибка', exc_info=ex)
        await state.clear()
        
    except Exception as ex:
        await to_thread(logger.exception,
            msg='При очистке состояния произошла ошибка', exc_info=ex)
        await state.clear() 