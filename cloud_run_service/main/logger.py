import logging

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", datefmt="%d-%b-%Y %H:%M:%S"
)
logger = logging.getLogger()
