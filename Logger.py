import logging

logging.basicConfig(
    filename = "debug.log",
    filemode = 'a',
    format = '(%(asctime)s); %(name)s; %(message)s',
    datefmt = '%H:%M:%S %d %B',
    level = logging.DEBUG
)

def log(message):
    logging.debug(message)
