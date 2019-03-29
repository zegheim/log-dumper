import re

from datetime import datetime, timedelta
from dateutil.parser import parse

from config import DAYFIRST, DEFAULT_RANGE, YEARFIRST
from logger import logger


# Decide which date format to use, based on user's configuration
def get_date_format():
    if DAYFIRST & (not YEARFIRST):
        return 'dd/MM/yyyy'
    elif DAYFIRST & YEARFIRST:
        return 'yyyy/dd/MM'
    elif (not DAYFIRST) & YEARFIRST:
        return 'yyyy/MM/dd'
    else:
        return 'MM/dd/yyyy'


# Check if an input is a date math operator
def is_date_math(date_str):
    if re.findall(r'\d+(\.\d+)?[yMwdhHms]', date_str):
        return True
    return False


# Get the date arguments from the string passed in -d
def get_date_args(date_arg):
    logger.debug('Parsing date arguments from \'{}\''.format(date_arg))

    date_from = None
    date_to = None
    date_range = None

    try:
        date_args = date_arg.split(':')
        # Assign date_arg to one of date_from, date_to, or date_range
        for idx, date_arg in enumerate(date_args):
            if is_date_math(date_arg):
                date_range = date_arg
            elif not idx:
                date_from = date_arg
            else:
                date_to = date_arg
    except AttributeError:
        # date_arg is None, so -d flag is not active
        logger.info('-d flag is not active.')

    return date_from, date_to, date_range


# Handles date arguments' logic
def date_handler(date_arg):
    fmt = get_date_format()
    logger.debug('Date format used: \'{}\''.format(fmt))
    date_from, date_to, date_range = get_date_args(date_arg)

    if ((date_to is not None) & (date_range is not None)):
        date_from = '{}||-{}/d'.format(date_to, date_range)
        date_to = '{}||/d'.format(date_to)
    elif ((date_from is not None)) & ((date_to is not None)):
        date_from = '{}||/d'.format(date_from)
        date_to = '{}||/d'.format(date_to)
    elif ((date_from is not None) & (date_range is not None)):
        date_to = '{}||+{}/d'.format(date_to, date_range)
        date_from = '{}||/d'.format(date_from)
    elif date_from is not None:
        date_from = '{}||/d'.format(date_from)
        date_to = date_from
    elif date_range is not None:
        date_to = 'now/s'
        date_from = 'now-{}/s'.format(date_range)
    else:
        date_to = 'now/s'
        date_from = 'now-{}/s'.format(DEFAULT_RANGE)

    logger.info('Searching logs from \'{}\' to \'{}\'.'
                .format(date_from, date_to))

    return date_from, date_to, fmt
