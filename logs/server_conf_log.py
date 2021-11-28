import logging
import os
import sys
import traceback
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import TimedRotatingFileHandler

from common.utils import get_log_file

server_logs_formatter = Formatter(f'%(asctime)-25s %(levelname)-10s %(module)-10s  %(message)s')

console_out_handler = StreamHandler(sys.stdout)
console_out_handler.setFormatter(server_logs_formatter)
console_out_handler.setLevel(logging.DEBUG)

log_file_handler = logging.handlers.TimedRotatingFileHandler(get_log_file('server.log'), when="D", interval=30,
                                                             backupCount=10,
                                                             encoding='utf8')
log_file_handler.setFormatter(server_logs_formatter)
log_file_handler.setLevel(logging.DEBUG)

logger = getLogger('app.server')
logger.addHandler(console_out_handler)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
