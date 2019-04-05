import re

from config import DAYFIRST, DEFAULT_RANGE, YEARFIRST
from logger import logger


# Decide which date format to use, based on user's configuration
def get_date_format():
    if DAYFIRST & (not YEARFIRST):
        date = 'dd/MM/yyyy'
    elif DAYFIRST & YEARFIRST:
        date = 'yyyy/dd/MM'
    elif (not DAYFIRST) & YEARFIRST:
        date = 'yyyy/MM/dd'
    else:
        date = 'MM/dd/yyyy'

    return '{} HH:mm:ss||{} HH:mm:ss||{}||{}' \
           .format(date[:-2], date, date[:-2], date)


# Check if an input is a date math operator
def is_date_math(date_str):
    if re.findall(r'\d+(\.\d+)?[yMwdhHms]', date_str):
        return True
    return False


# Get the date arguments from the string passed in -d
def get_date_args(date_arg):
    logger.debug('Parsing date arguments from {}'.format(date_arg))

    date_from = None
    date_to = None
    date_range = None

    try:
        date_arg = ' '.join(date_arg)
        date_args = date_arg.split(', ')
        # Assign date_arg to one of date_from, date_to, or date_range
        for idx, date_arg in enumerate(date_args):
            if is_date_math(date_arg):
                date_range = date_arg
            elif not idx:
                date_from = date_arg
            else:
                date_to = date_arg
    except (TypeError, AttributeError):
        # date_arg is None, so -d flag is not active
        logger.info('-d flag is not active.')

    return date_from, date_to, date_range


# Handles date arguments' logic. See https://bit.ly/2Ovs2Cl for more info.
def date_handler(date_arg):
    fmt = get_date_format()
    logger.debug('Date format used: \'{}\''.format(fmt))
    date_from, date_to, date_range = get_date_args(date_arg)

    if ((date_to is not None) & (date_range is not None)):
        # Search from (date_to - date_range) to date_to
        date_from = '{}||-{}'.format(date_to, date_range)
        date_to = '{}||'.format(date_to)
    elif ((date_from is not None)) & ((date_to is not None)):
        # Search from date_from to date_to
        date_from = '{}||'.format(date_from)
        date_to = '{}||'.format(date_to)
    elif ((date_from is not None) & (date_range is not None)):
        # Search from date_from to (date_from + date_range)
        date_to = '{}||+{}'.format(date_to, date_range)
        date_from = '{}||'.format(date_from)
    elif date_from is not None:
        # Search from beginning of date_from (00:00:00)
        # to end of date_from (23:59:59.999999)
        date_from = '{}||'.format(date_from)
        date_to = date_from
    elif date_range is not None:
        # Search from (now - date_range) to now
        date_to = 'now/s'
        date_from = 'now-{}/s'.format(date_range)
    else:
        # Search from (now - DEFAULT_RANGE) to now
        date_to = 'now/s'
        date_from = 'now-{}/s'.format(DEFAULT_RANGE)

    # Check if date_to / date_from does not contain "now" or ":"
    # (time string). If it does not, then we round it by a day.
    if not any(x in date_to for x in [':', 'now']):
        date_to += '/d'

    if not any(x in date_from for x in [':', 'now']):
        date_from += '/d'

    logger.info('Searching e-mails from \'{}\' to \'{}\'.'
                .format(date_from, date_to))

    return date_from, date_to, fmt
