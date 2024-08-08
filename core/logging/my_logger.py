import logging
import os



class MyLogger():
    """
    ## Логгирование
    
    ### Args:
        - name (str) = Название логгера. По умолчанию: 'my_logger'.
        - log_file (str) = Путь к файлу.\
            По умолчанию: 'os.path.join('core', 'logs', 'loggs_file.log')'.
        - console (bool): Режим работы логгера. Если True, то выводит информацию в консоль.\
        Если False, выводит информацию в файл, который указан в переменной self.log_file

    ### Зависимости:
        - import os, logging

    ### Пример использования:
        - from core.logs.my_logger import MyLogger
        - logger = MyLogger(name='main_py_logger').get_logger()

        try:
            pass
        except Exception as ex:
            logger.error(msg='Произошла ошибка: ', exc_info=ex)
            logging.debug('ДЕБАГ')
            logging.info('INFO')
            logging.warning('ВАРНИНГ')
            logging.error('ОШИБКА')
            logging.critical('КРИТИЧЕСКАЯ ОШИБКА')
    """
    def __init__(
            self,
            name: str = 'my_logger',
            log_file:str = os.path.join('core', 'logs', 'loggs_file.log'),
            is_console:bool = True
        ) -> None:
        self.logger = logging.getLogger(name)
        self.logs_dir:str = os.path.join('core', 'logs')
        self.log_file:str = log_file  # Файл для логов
        self.is_console:bool = is_console  # Вывод в консоль или в файл
        self._create_logs_dir()
        self._configure_logger()

    def _create_logs_dir(self) -> None:
        """
        ## Создаёт директорию для логфайла, если она не существует.
        ### Вызывается при объявлении класса MyLogger
        """
        if not os.path.exists(self.logs_dir):
            os.mkdir(self.logs_dir)

    def _configure_logger(self) -> None:
        """ 
        ## Настраивает логгер в зависимости от режима работы (консоль или файл).
        """
        if self.is_console:
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(self.log_file, encoding='utf-8')

        formatter = logging.Formatter(
            '%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
            datefmt='%d/%m/%Y %I:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_logger(self) -> logging.Logger:
        """ ## Возвращает настроенный логгер."""

        return self.logger