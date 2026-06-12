"""
Lightweight file logger. The UI owns the terminal (curses), so logging to stdout would corrupt
the display. Instead everything goes to a rotating log file next to the config.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE_LOCATION = os.path.join(os.path.dirname(__file__), "../../equity_tracker.log")

_logger = logging.getLogger("equity_tracker")

if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    _handler = RotatingFileHandler(LOG_FILE_LOCATION, maxBytes=1_000_000, backupCount=3)
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _logger.addHandler(_handler)
    _logger.propagate = False


def log(msg):
    _logger.info(msg)
