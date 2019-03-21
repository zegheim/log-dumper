#!/usr/bin/python

import argparse
import os
import sys

from datetime import date, datetime, time, timedelta
from elasticsearch import Elasticsearch, ElasticsearchException
from elasticsearch_dsl import Q, Search

from config import es_server, help
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



# Driver programme
def main(args):
    pass

if __name__ == '__main__':
    # Define command line arguments' structure
    parser = argparse.ArgumentParser(description=help['desc'])
    parser.add_argument('index', help=help['index'])
    parser.add_argument('-d', '--date', dest='date', default=None,
                        metavar='<DATE_ARG>', help=help['d'])
    parser.add_argument('-m' '--module', dest='module',
                        default='system', metavar='<MODULE>', help=help['m'])
    parser.add_argument('-p', '--program', dest='program',
                        metavar='<PROGRAM>', help=help['p'])
    parser.add_argument('-s', '--source', dest='source',
                        default='/var/log/messages', metavar='<PATH/TO/LOG>',
                        help=help['s'])
    parser.add_argument('-t', '--tier', dest='tier',
                        choices=['live', 'dev', 'test'], metavar='<TIER>',
                        help=help['t'])

    # Parse arguments
    args = parser.parse_args()

    main(args)
