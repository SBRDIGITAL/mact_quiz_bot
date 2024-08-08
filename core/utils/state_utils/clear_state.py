from asyncio import to_thread

from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from core.logging.my_logger import MyLogger


logger = MyLogger(name='clear_state_logger', is_console=False).get_logger()


async def clear_state(state: FSMContext) -> None:
    """ ## Очищает состояние если оно есть """
    try:
        this_state = await state.get_state()
        if this_state:
            await state.clear()
    
    except TelegramBadRequest as ex:
        await to_thread(logger.exception,
            msg='При очистке состояния произошла ошибка', exc_info=ex)
        await state.clear()
        
    except Exception as ex:
        await to_thread(logger.exception,
            msg='При очистке состояния произошла ошибка', exc_info=ex)
        await state.clear() 