#!/usr/bin/python

import errno
import logging
import os

from config import LOG_LEVEL

# Instantiate a logger to log all errors
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Define how we format our log messages
fmt_ch = logging.Formatter('[%(levelname)s]: %(message)s')
fmt_fh = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

# Create a handler that outputs logs events with
# severity level WARNING and above to console
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(fmt_ch)

# Attempt to create the directory `logs` if it does not exist
try:
    os.makedirs('logs')
except OSError as exc:
    if exc.errno is errno.EEXIST and os.path.isdir('logs'):
        pass
    else:
        raise

# Create a handler that outputs all logs events to es.log
fh = logging.FileHandler('logs/log-dumper.log', mode='w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt_fh)

# Add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
