import logging
import os
import sys
import traceback
from logging import getLogger, StreamHandler, Formatter

log_file_path = os.path.join('logs', 'client_logs', 'client.log')
module = traceback.format_stack()[0].strip().split()[1]
module = module[module.rfind('\\') + 1: -5]
client_logs_formatter = Formatter(f'%(asctime)-25s %(levelname)-10s {module}  %(message)s')

console_out_handler = StreamHandler(sys.stdout)
console_out_handler.setFormatter(client_logs_formatter)
console_out_handler.setLevel(logging.DEBUG)

log_file_handler = logging.FileHandler(log_file_path, encoding='utf8')
log_file_handler.setFormatter(client_logs_formatter)
log_file_handler.setLevel(logging.DEBUG)

logger = getLogger('app.client')
logger.addHandler(console_out_handler)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
