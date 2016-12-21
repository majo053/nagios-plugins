#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2016-12-20 17:30:59 +0000 (Tue, 20 Dec 2016)
#
#  https://github.com/harisekhon/nagios-plugins
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/harisekhon
#

"""

Nagios Plugin to check RabbitMQ aliveness built-in check on the given node via its Management REST API

This check declares a test queue, then publishes and consumes a message and returns the status of the check.

Requires the management plugin to be loaded.

For a similar check see check_rabbitmq.py which does this via the native AMQP API with a high degree of configurability
as well as performance data timings for each action.

Tested on RabbitMQ 3.6.6 (does not work on RabbitMQ <= 3.5)

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import traceback
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import getenvs, validate_chars
    from harisekhon import RestNagiosPlugin
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.1'


class CheckRabbitMQAliveness(RestNagiosPlugin):

    def __init__(self):
        # Python 2.x
        super(CheckRabbitMQAliveness, self).__init__()
        # Python 3.x
        # super().__init__()
        self.name = 'RabbitMQ'
        self.default_port = 15672
        self.default_user = 'guest'
        self.default_password = 'guest'
        self.default_vhost = '/'
        self.vhost = self.default_vhost
        self.path = 'api/aliveness-test/' # add vhost
        self.json = True
        self.msg = 'msg not defined yet'

    def add_options(self):
        super(CheckRabbitMQAliveness, self).add_options()
        self.add_opt('-O', '--vhost', default=getenvs('RABBITMQ_VHOST', default=self.default_vhost),
                     help='{0} VHost to check ($RABBITMQ_VHOST, default: /)')

    def process_options(self):
        super(CheckRabbitMQAliveness, self).process_options()
        self.vhost = self.get_opt('vhost')
        validate_chars(self.vhost, 'vhost', r'/\w\+-')
        self.path += self.vhost.lstrip('/')

    def parse_json(self, json_data):
        status = json_data['status']
        self.msg = "{0} aliveness status = '{1}'".format(self.name, status)
        if status != 'ok':
            self.critical()
            if 'reason' in json_data:
                self.msg += ", reason = '{0}'".format(json_data['reason'])


if __name__ == '__main__':
    CheckRabbitMQAliveness().main()
