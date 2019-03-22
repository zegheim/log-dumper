#!/usr/bin/python

import argparse
import os
import pprint
import sys

from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch_dsl import Q, Search

from config import DOC_SIZE, es_server, help
from date_handler import date_handler
from logger import logger


# Instantiate an Elasticsearch client with the required settings
def init_elastic(user, password):
    auth_values = (user, password)
    es = Elasticsearch([es_server['base_url']],
                       use_ssl=True,
                       verify_certs=True,
                       ca_certs=es_server['crt_path'],
                       http_auth=auth_values)
    return es


# Query Elasticsearch with the relevant parameters
def search_logs(client, index, module, source, date_arg, program, tier):
    # Create a range filter dict (date)
    date_from, date_to = date_handler(date_arg)
    date_filter = {'gte': date_from, 'lte': date_to}
    logger.info('Searching logs from {} to {}.'.format(date_from, date_to))

    # Pad a wildcard character behind index
    index = index + '*'

    # Create a term filter dict (tier, module, source, and program)
    term_filter = {'ed.tier': tier,
                   'fileset.module': module,
                   'source': source}
    if program is not None:
        term_filter['system.syslog.program'] = program

    logger.info('Searching logs satisfying '
                'ed.tier = {}, '
                'fileset.module = {}, '
                'source = {}, '
                'system.syslog.program = {}.'
                .format(tier, module, source, program))

    # Instantiate a Search object
    s = Search(using=client, index=index) \
        .source(['system.syslog.hostname',
                 'system.syslog.message',
                 'system.syslog.pid',
                 'system.syslog.program',
                 'system.syslog.timestamp']) \
        .sort('system.syslog.timestamp') \
        .filter('range', system__syslog__timestamp=date_filter) \
        .filter('term', **term_filter) \
        .extra(size=DOC_SIZE)

    # Pretty print our search object for logging / debugging purposes
    # pprint_s = json.dumps(s.to_dict(), indent=4)
    logger.debug('Created search object s: {}'.format(s.to_dict()))

    # Send our query to Elasticsearch and return the response
    response = s.execute()
    logger.debug('Got response: {}'.format(response))

    return response


# Driver programme
def main(args):
    logger.debug('Received arguments: {}'.format(args))

    # Create an Elasticsearch instance
    es = init_elastic(es_server['username'], es_server['password'])

    # Pad a wildcard character behind index
    index = args.index + '*'

    logs = search_logs(es, index, args.module,
                       args.source, args.date,
                       args.program, args.tier)

    for hit in logs:
        print(hit)

if __name__ == '__main__':
    # Define command line arguments' structure
    parser = argparse.ArgumentParser(description=help['desc'])
    parser.add_argument('index', help=help['index'])
    parser.add_argument('-d', dest='date', default=None,
                        metavar='<DATE_ARG>', help=help['d'])
    parser.add_argument('-m', dest='module', default='system',
                        metavar='<MODULE>', help=help['m'])
    parser.add_argument('-p', dest='program', default=None,
                        metavar='<PROGRAM>', help=help['p'])
    parser.add_argument('-s', dest='source', default='/var/log/messages',
                        metavar='<PATH/TO/LOG>', help=help['s'])
    parser.add_argument('-t', dest='tier', choices=['live', 'dev', 'test'],
                        metavar='<SERVER TIER>', help=help['t'])

    # Parse arguments
    args = parser.parse_args()

    main(args)
