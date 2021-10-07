import inspect
import logging
import sys
import traceback
import logs.client_conf_log
import logs.server_conf_log

if sys.argv[0].find('server') >= 0:
    logger = logging.getLogger('app.server')
else:
    logger = logging.getLogger('app.client')


class SystemLogger:
    def __call__(self, func):
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            logger.debug(f'Вызвана функция с именем: {func.__name__}. Параметры функции: {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}.{traceback.format_stack()[0].strip().split()[-1]}.'
                         f'Вызов из функции {inspect.stack()[1][3]}')
            return result
        return wrap
