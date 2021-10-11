import inspect
import logging
import sys
import traceback
import logs.client_conf_log
import logs.server_conf_log


class SystemLogger:
    def __init__(self):
        if sys.argv[0].find('server') >= 0:
            self.logger = logging.getLogger('app.server')
        else:
            self.logger = logging.getLogger('app.client')

    def __call__(self, func):
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            self.logger.debug(f'Вызвана функция с именем: {func.__name__}, аргументы функции: {args}, {kwargs}. '
                              f'Вызов из модуля {func.__module__}.{traceback.format_stack()[0].strip().split()[-1]}.'
                              f'Вызов из {inspect.stack()[1][0]}')
            return result
        return wrap
