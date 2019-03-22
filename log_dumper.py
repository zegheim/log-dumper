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
    logger.info('Searching logs from {} satisfying '
                'ed.tier = {}, '
                'fileset.module = {}, '
                'source = {}, '
                'system.syslog.program = {}.'
                .format(index, tier, module, source, program))

    # Create a range filter dict (date)
    date_from, date_to = date_handler(date_arg)
    date_filter = {'gte': date_from, 'lte': date_to}
    logger.info('Searching logs from {} to {}.'.format(date_from, date_to))

    # Create a match query object (module, source, program, tier)
    query_list = [Q('match', fileset__module=module), Q('match', source=source)]
    if tier is not None:
        query_list.append(Q('match', ed__tier=tier))
    if program is not None:
        query_list.append(Q('match', system__syslog__program=program))
    query_obj = Q('bool', must=query_list)

    # Instantiate a Search object
    s = Search(using=client, index=index) \
        .source(['system.syslog.hostname',
                 'system.syslog.message',
                 'system.syslog.pid',
                 'system.syslog.program',
                 'system.syslog.timestamp']) \
        .sort('system.syslog.timestamp') \
        .query(query_obj) \
        .filter('range', system__syslog__timestamp=date_filter) \
        .extra(size=DOC_SIZE)
    logger.debug('Created search object s: {}'.format(s.to_dict()))

    # Send our query to Elasticsearch and return the response
    r = s.execute()
    logger.debug('Found {} hits in response: {}'.format(r.hits.total, r))

    return r


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
        syslog = hit.system.syslog
        try:
            print('{} {} {}[{}]: {}'.format(syslog.timestamp,
                                            syslog.hostname,
                                            syslog.program,
                                            syslog.pid,
                                            syslog.message))
        except AttributeError:
            logger.warning('pid not found for {}/{}/{}'
                           .format(hit.meta.index,
                                   hit.meta.doc_type,
                                   hit.meta.id))
            print('{} {} {}: {}'.format(syslog.timestamp,
                                        syslog.hostname,
                                        syslog.program,
                                        syslog.message))

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
