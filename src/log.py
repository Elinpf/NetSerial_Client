import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh_formatter = logging.Formatter(
    '%(asctime)-6s: - %(levelname)s - %(message)s')
sh_formatter = logging.Formatter('[%(levelname)s] %(message)s')

# to file
fh = logging.FileHandler('console.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fh_formatter)

# to screen
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(sh_formatter)

# add Handler
logger.addHandler(fh)
logger.addHandler(sh)

logger.info("============= Start New Process =============")
