import inspect
import logging
import sys
import traceback

if sys.argv[0].find('server') >= 0:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


class SystemLogger:
    def __call__(self, func):
        def wrap(*args, **kwargs):
            """Обертка"""
            result = func(*args, **kwargs)
            logger.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}. Вызов из'
                         f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                         f'Вызов из функции {inspect.stack()[1][3]}')
            return result

        return wrap
