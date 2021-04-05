#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
The latest version of this package is available at:
<http://github.com/jantman/psread>

################################################################################
Copyright 2021 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of psread, also known as psread.

    psread is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    psread is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with psread.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/psread> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import sys
import os
import argcomplete
import argparse
import logging
from typing import Dict, List, Set
import re
from time import time
import pickle
from appdirs import user_cache_dir

import boto3
from botocore.client import BaseClient

FORMAT: str = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger: logging.Logger = logging.getLogger()

VERSION: str = '0.1.1'
PROJECT_URL: str = 'https://github.com/jantman/psread'
CACHE_DIR: str = os.path.join(
    user_cache_dir('psread', 'jantman'), 'psread.pkl'
)

bashcode: str = r'''
# Run something, muting output or redirecting it to the debug stream
# depending on the value of _ARC_DEBUG.
__psread_argcomplete_run() {
    if [[ -z "$_ARC_DEBUG" ]]; then
        "$@" 8>&1 9>&2 1>/dev/null 2>&1
    else
        "$@" 8>&1 9>&2 1>&9 2>&1
    fi
}
_psread_argcomplete() {
    local IFS=$'\013'
    local SUPPRESS_SPACE=0
    if compopt +o nospace 2> /dev/null; then
        SUPPRESS_SPACE=1
    fi
    COMPREPLY=( $(IFS="$IFS" \
                  COMP_LINE="$COMP_LINE" \
                  COMP_POINT="$COMP_POINT" \
                  COMP_TYPE="$COMP_TYPE" \
                  _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" \
                  _ARGCOMPLETE=1 \
                  _ARGCOMPLETE_SUPPRESS_SPACE=$SUPPRESS_SPACE \
                  __psread_argcomplete_run "$1") )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    elif [[ $SUPPRESS_SPACE == 1 ]] && [[ "$COMPREPLY" =~ [=/:]$ ]]; then
        compopt -o nospace
    fi
}
complete -o nospace -o default -F _psread_argcomplete psread
'''


class PSClient:

    TOPLEVEL_RE = re.compile(r'^/[^/]+/?$')
    KEY_RE = re.compile(r'[^/]+/?$')
    CACHE_TTL = int(os.environ.get('PSREAD_CACHE_TTL', '86400'))

    def __init__(self):
        self._acct_id: str = self._get_account_id()
        self._region: str = boto3.client('sts')._client_config.region_name
        logger.debug(
            'Connected to account %s region %s',
            self._acct_id, self._region
        )
        logger.debug('Connecting to SSM')
        self._ssm = boto3.client('ssm')
        self._cache_path = os.environ.get('PSREAD_CACHE_PATH', CACHE_DIR)
        logger.debug('Cache path: %s', self._cache_path)
        self._params = self._load_cache()
        logger.debug('Loaded %d params from cache', len(self._params))

    def _get_account_id(self) -> str:
        logger.debug('calling sts:GetCallerIdentity')
        sts: BaseClient = boto3.client('sts')
        cid: Dict[str, str] = sts.get_caller_identity()
        logger.debug('caller identity: %s', cid)
        return cid['Account']

    def complete_actions(self, **kwargs: dict) -> List[str]:
        if kwargs['action'].dest != 'ACTION':
            return []
        return ['ls', 'read', 'get']

    def complete_params(self, **kwargs: dict) -> List[str]:
        if kwargs['action'].dest != 'PARAM':
            return []
        if kwargs['parsed_args'].ACTION is None:
            return []
        if kwargs['prefix'] == '':
            kwargs['prefix'] = '/'
        return self._get_params_under(kwargs['prefix'])

    def _get_params_under(self, prefix: str) -> List[str]:
        result: List[str] = []
        p: str
        for p in self._params:
            if not p.startswith(prefix):
                continue
            r: str = p[len(prefix):].lstrip('/')
            if r.find('/') in [-1, len(r) - 1]:
                result.append(p)
        return result

    def _load_cache(self, recache: bool = False):
        cache = {}
        if os.path.exists(self._cache_path):
            logger.debug('Reading %s', self._cache_path)
            with open(self._cache_path, 'rb') as f:
                cache = pickle.load(f)
        if self._acct_id not in cache:
            cache[self._acct_id] = {}
        if self._region not in cache[self._acct_id]:
            cache[self._acct_id][self._region] = {}
        c = cache[self._acct_id][self._region]
        if time() - c.get('ts', 0) <= self.CACHE_TTL and not recache:
            return c['params']
        logger.warning(
            f'Re-caching parameters for %s %s ; this may take some time',
            self._acct_id, self._region
        )
        cache[self._acct_id][self._region] = {
            'ts': time(),
            'params': self._get_param_names()
        }
        d = os.path.dirname(self._cache_path)
        if not os.path.exists(d):
            logger.debug('makedirs: %s', d)
            os.makedirs(d)
        logger.debug('Writing %s', self._cache_path)
        with open(self._cache_path, 'wb') as f:
            pickle.dump(cache, f, pickle.HIGHEST_PROTOCOL)
        return cache[self._acct_id][self._region]['params']

    def _get_param_names(self) -> List[str]:
        result: Set[str] = set()
        logger.debug('Paginating DescribeParameters')
        paginator = self._ssm.get_paginator('describe_parameters')
        for page in paginator.paginate():
            for param in page['Parameters']:
                result.add(param['Name'])
                parts = param['Name'].split('/')[1:]
                for i in range(1, len(parts)):
                    result.add('/' + '/'.join(parts[0:i]) + '/')
        return sorted(list(result))

    def do_list(self, param: str):
        for p in self._get_params_under(param):
            print(p)

    def do_read(self, param: str):
        if not param.endswith('/'):
            p = self._ssm.get_parameter(Name=param, WithDecryption=True)
            print(f'{param}\t{p["Parameter"]["Value"]}')
            return
        paginator = self._ssm.get_paginator('get_parameters_by_path')
        result = {}
        for page in paginator.paginate(
            Path=param, Recursive=False, WithDecryption=True, MaxResults=10
        ):
            for p in page['Parameters']:
                result[p['Name']] = p['Value']
        for k, v in sorted(result.items()):
            print(f'{k}\t{v}')


def bash_wrapper() -> str:
    """
    Return the string bash wrapper function to execute this command and
    evaluate the STDOUT.

    :return: bash wrapper function for this command
    :rtype: str
    """
    p: str = os.path.realpath(__file__)
    code: str = bashcode % dict(
        interpreter=sys.executable,
        script=p
    )
    return code


def parse_args(client) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description='Quick, simple AWS Parameter Store CLI for listing/reading'
                    ' params with tab completion',
        add_help=False
    )
    p.add_argument('-h', '--help', dest='help', action='store_true',
                   default=False, help='show this help message and exit')
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-w', '--bash-wrapper', dest='bash_wrapper',
                   action='store_true', default=False, help='print bash wrapper'
                   ' function to STDOUT and exit')
    p.add_argument('-V', '--version', action='version',
                   help='Print version number and exit',
                   version=f'psread v{VERSION} <{PROJECT_URL}> '
                           f'(cache: {CACHE_DIR})')
    p.add_argument('-R', '--recache', dest='recache', action='store_true',
                   default=False,
                   help='re-cache parameters for this region of this account ')
    p.add_argument('--called-from-wrapper', dest='wrapper_called',
                   action='store_true', default=False, help='DO NOT USE')
    p.add_argument(
        'ACTION', action='store', type=str, default=None, nargs='?',
        help='Action to perform', choices=['ls', 'read', 'get']
    ).completer = client.complete_actions
    p.add_argument(
        'PARAM', action='store', type=str, default=None,
        help='Parameter (or parameter path) to list or read', nargs='?'
    ).completer = client.complete_params
    argcomplete.autocomplete(p, always_complete_options=False)
    args = p.parse_args()
    if args.help:
        p.print_help(sys.stderr)
        raise SystemExit(1)
    return args


def set_log_info(l: logging.Logger):
    """set logger level to INFO"""
    set_log_level_format(
        l, logging.INFO,
        '%(asctime)s %(levelname)s:%(name)s:%(message)s'
    )


def set_log_debug(l: logging.Logger):
    """set logger level to DEBUG, and debug-level output format"""
    set_log_level_format(
        l,
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(l: logging.Logger, level: int, format: str):
    """
    Set logger level and format.

    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    l.handlers[0].setFormatter(formatter)
    l.setLevel(level)


def main():
    if os.environ.get('PSREAD_LOG') == 'DEBUG':
        set_log_debug(logger)
    client: PSClient = PSClient()
    args: argparse.Namespace = parse_args(client)
    # set logging level
    if args.verbose > 1:
        set_log_debug(logger)
    elif args.verbose == 1:
        set_log_info(logger)
    if args.bash_wrapper:
        sys.stdout.write(bash_wrapper())
        raise SystemExit(1)
    if args.recache:
        client._load_cache(recache=True)
    if args.ACTION in ['read', 'get']:
        client.do_read(args.PARAM)
    else:
        client.do_list(args.PARAM)


if __name__ == "__main__":
    main()
