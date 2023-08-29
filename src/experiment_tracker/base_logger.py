"""
This file contains the logger used for tracking the library.
"""

# Logging
import logging
import coloredlogs 
coloredlogs.install()
logger = logging.getLogger(__name__)
# stream = logging.StreamHandler()
# LOG_LEVEL = logging.INFO
# stream.setLevel(LOG_LEVEL)
# logger.addHandler(stream)