import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, format='<green>[{time}] [{elapsed}]</green> <level>[{file}: {line}] > {message}</level>')
logger.add('logs/script.log', mode='w', format='[{time}] [{elapsed}] [{name}: {line}] > {message}')
