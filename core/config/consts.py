from typing import Dict
from os.path import join

CORE_DIR_PATH:str = join('core')
DATA_DIR_PATH:str = join(CORE_DIR_PATH, 'data')

TEXT_ANSWERS_TXT:Dict[str, str] = {
    "main_menu_txt": ', приветствую и желаю прекрасного настроения!\nЧтобы ответить на вопросы, которые меня интересуют о чат-боте на сайте https://gk-mact.ru, нажмите на кнопку ниже 👇'
}