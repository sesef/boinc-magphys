#! /usr/bin/env python2.7
#
#    (c) UWA, The University of Western Australia
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA, 2012
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
"""
Archive the stats stored in .../html/stats_archive to S3
"""
import logging
import os
import sys

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)

# Setup the Python Path as we may be running this via ssh
base_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(base_path, '..')))
sys.path.append(os.path.abspath(os.path.join(base_path, '../../../../boinc/py')))

import argparse
from archive.archive_boinc_stats_mod import process_ami, process_boinc
from utils.sanity_checks import pass_sanity_checks

parser = argparse.ArgumentParser('Archive BOINC statistics to S3')
parser.add_argument('option', choices=['boinc','ami'], help='are we running on the BOINC server or the AMI server')
args = vars(parser.parse_args())


if args['option'] == 'boinc':
    LOG.info('PYTHONPATH = {0}'.format(sys.path))
    # We're running from the BOINC server
    process_boinc()
else:
    # We're running from a specially created AMI
    logging_file_handler = logging.FileHandler('')
    LOG.addHandler(logging_file_handler)
    LOG.info('PYTHONPATH = {0}'.format(sys.path))

    if pass_sanity_checks(logging_file_handler):
        process_ami(logging_file_handler)