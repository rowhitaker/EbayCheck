import logging
import os
from datetime import datetime as DT

import archiver


def build_logger(name, level):
    # archive previous logs
    archiver.archive_files()

    # Logging initialization
    logger = logging.getLogger(name)
    log_dir = 'Logs'

    if level.upper() == 'DEBUG':
        level = logging.DEBUG
    elif level.upper() == 'INFO':
        level = logging.INFO
    elif level.upper() == 'WARNING':
        level = logging.WARNING
    elif level.upper() == 'ERROR':
        level = logging.ERROR
    elif level.upper() == 'CRITICAL':
        level = logging.CRITICAL

    date_format = '%Y%m%d'
    date = DT.now().strftime(date_format)
    time = DT.now().strftime('%H%M%S%f')

    # create our log folders if they don't already exist
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    # build logger
    file_hdlr = logging.FileHandler('./{}/{}_{}_{}.{}'.format(log_dir, name, date, time, 'log'))
    formatter = logging.Formatter(fmt='%(asctime)s  %(levelname)-8s %(message)s',
                                  datefmt='%Y%m%d_%H%M%S')
    file_hdlr.setFormatter(formatter)
    logger.addHandler(file_hdlr)
    logger.setLevel(level)
    logger.current_step = None

    def set_step(current_step):
        current_step = current_step.replace(' ', '_').upper()
        step_length = len(current_step) + 58
        logger.critical('*' * step_length)
        logger.critical('{0} Beginning Step: {1} {0}'.format('*' * 20, current_step))
        logger.critical('*' * step_length)

    def close():
        completed_message = 'Closing down logger, Thanks for playing :-)'
        message_length = len(completed_message) + 26
        logger.critical('*' * message_length)
        logger.critical('{0} {1} {0}'.format('*' * 12, completed_message))
        logger.critical('*' * message_length)
        logging.shutdown()

    set_step('Init')
    logger.critical('Initializing logger')
    logger.set_step = set_step
    logger.close = close

    return logger


