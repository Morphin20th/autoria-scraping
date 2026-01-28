import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s|\t%(message)s\t| %(asctime)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("autoria-scrape")
