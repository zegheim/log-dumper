from datetime import datetime, timedelta
from dateutil.parser import parse

from config import DAYFIRST, RANGE_LIMIT, YEARFIRST
from logger import logger


# Get the date arguments from the string passed in -d
def get_date_arguments(date_arg):
    logger.debug('Parsing date arguments from \'{}\''.format(date_arg))

    date_from = None
    date_to = None
    date_range = None

    try:
        date_args = date_arg.split(':')
        # Assign date_arg to one of date_from, date_to, or date_range
        for idx, date_arg in enumerate(date_args):
            if is_date_type(date_arg, 'range'):
                date_range = int(date_arg)
                logger.info('Found date_range: \'{}\''.format(date_range))
            elif ((idx == 0) and is_date_type(date_arg, 'date')):
                date_from = date_arg
                logger.info('Found date_from: \'{}\''.format(date_from))
            elif is_date_type(date_arg, 'date'):
                date_to = date_arg
                logger.info('Found date_to: \'{}\''.format(date_to))
            else:
                logger.error('Could not parse \'{}\'.'.format(date_arg))
    except (AttributeError, TypeError):  # date_arg is None
        logger.info('-d flag is not active.')

    return date_from, date_to, date_range


# Check if date_arg is of the given type. Returns True / False
def is_date_type(date_arg, arg_type):
    try:
        if arg_type == 'range':
            logger.debug
            # Check that date_arg is below RANGE_LIMIT
            return int(date_arg) <= RANGE_LIMIT
        elif arg_type == 'date':
            # Check if parse_date(arg) throws ValueError
            parse_date(date_arg)
    except ValueError:
        return False

    return True


# Handles date arguments' logic
def date_handler(date_arg):
    date_from, date_to, date_range = get_date_arguments(date_arg)

    if date_range is None:
        # No date range is given, defaults to today
        date_range = 0

    if ((date_to is not None) & (date_from is not None)):
        # Both dates are given, fuzzily parse both
        date_from = parse_date(date_from)
        date_to = parse_date(date_to)
    elif ((date_to is None) & (date_from is not None)):
        # Only the lower bound is given, upper bound defaults to one day after
        date_from = parse_date(date_from)
        date_to = date_from + timedelta(days=date_range)
    elif ((date_from is None) & (date_to is not None)):
        # Only the upper bound is given, lower bound defaults to yesterday
        date_to = parse_date(date_to)
        # Search x days before date_to
        date_from = date_to - timedelta(days=date_range)
    else:
        # No date argument is given, defaults to all e-mails in the last day
        date_to = datetime.now()
        date_from = date_to - timedelta(days=date_range)

    # Expand our search range from 00:00:00 of
    # date_from to 23:59:59.99999 of date_to
    date_to = date_to.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
    date_from = date_from.replace(hour=0, minute=0,
                                  second=0, microsecond=0)

    return date_from, date_to


# Parse dates according to the specified configuration
def parse_date(date, **kwargs):
    return parse(date, dayfirst=DAYFIRST, yearfirst=YEARFIRST, **kwargs)
