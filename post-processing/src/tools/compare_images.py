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
Compare two images and build a multi-layered fits image of the results
"""
from __future__ import print_function
import argparse
import logging
import math
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_
from config import DB_LOGIN
from database.database_support_core import GALAXY, PIXEL_RESULT, PIXEL_PARAMETER
from utils.writeable_dir import WriteableDir

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)

parser = argparse.ArgumentParser('Build images by comparing two galaxies')
parser.add_argument('-o','--output_dir', action=WriteableDir, nargs=1, help='where the image will be written')
parser.add_argument('galaxy_id', nargs='*', type=int, help='the galaxy_ids of the galaxies to compare')
args = vars(parser.parse_args())

OUTPUT_DIRECTORY = args['output_dir']
IMAGE_NAMES_AE = ['i_sfh', 'i_ir']
LEN_NAMES_AE = len(IMAGE_NAMES_AE)
IMAGE_NAMES_MSE = ['fmu_sfh', 'fmu_ir', 'mu', 's_sfr', 'm', 'ldust', 'mdust', 'sfr']
LEN_NAMES_MSE = len(IMAGE_NAMES_MSE)

PARAMETER_NUMBERS = [1, 2, 3, 5, 6, 7, 15, 16]

# First check the galaxy exists in the database
engine = create_engine(DB_LOGIN)
connection = engine.connect()

class Galaxy:
    """
    A galaxy
    """
    def __init__(self, galaxy_details):
        self.galaxy_id = galaxy_details[GALAXY.c.galaxy_id]
        self.name = galaxy_details[GALAXY.c.name]
        self.dimension_x = galaxy_details[GALAXY.c.dimension_x]
        self.dimension_y = galaxy_details[GALAXY.c.dimension_y]

galaxy_details = []
for galaxy in connection.execute(select([GALAXY]).where(GALAXY.c.galaxy_id.in_(args['galaxy_id']))):
    galaxy_details.append(Galaxy(galaxy))

if len(galaxy_details) != 2:
    LOG.error('%d galaxies found', len(galaxy_details))
    exit(1)

if galaxy_details[0].dimension_x != galaxy_details[1].dimension_x or galaxy_details[0].dimension_y != galaxy_details[1].dimension_y:
    LOG.error('The galaxies are different sizes (%d x %d) vs (%d x %d)', galaxy_details[0].dimension_x, galaxy_details[0].dimension_y, galaxy_details[1].dimension_x, galaxy_details[1].dimension_y)
    exit(1)

array01 = [[[[None, None] for depth in range(LEN_NAMES_AE + (LEN_NAMES_MSE * 3))] for col in range(galaxy_details[0].dimension_y)] for row in range(galaxy_details[0].dimension_x)]

# Load the data
for i in range(2):
    for pixel in connection.execute(select([PIXEL_RESULT]).where(PIXEL_RESULT.c.galaxy_id == galaxy_details[i].galaxy_id)):
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][0][i] = pixel[PIXEL_RESULT.c.i_sfh]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][1][i] = pixel[PIXEL_RESULT.c.i_ir]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][2][i] = pixel[PIXEL_RESULT.c.fmu_sfh]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][3][i] = pixel[PIXEL_RESULT.c.fmu_ir]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][4][i] = pixel[PIXEL_RESULT.c.mu]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][5][i] = pixel[PIXEL_RESULT.c.s_sfr]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][6][i] = pixel[PIXEL_RESULT.c.m]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][7][i] = pixel[PIXEL_RESULT.c.ldust]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][8][i] = pixel[PIXEL_RESULT.c.mdust]
        array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][9][i] = pixel[PIXEL_RESULT.c.sfr]

        j = 10
        for pixel_parameter in connection.execute(select([PIXEL_PARAMETER])
            .where(and_(PIXEL_PARAMETER.c.pxresult_id == pixel[PIXEL_RESULT.c.pxresult_id], PIXEL_PARAMETER.c.parameter_name_id.in_(PARAMETER_NUMBERS)))
            .order_by(PIXEL_PARAMETER.c.parameter_name_id)):
            array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][j][i] = pixel_parameter[PIXEL_PARAMETER.c.percentile50]
            j += 1
            array01[pixel[PIXEL_RESULT.c.x]][pixel[PIXEL_RESULT.c.y]][j][i] = pixel_parameter[PIXEL_PARAMETER.c.high_prob_bin]

absolute_error = [0 for x in range(LEN_NAMES_AE)]
mean_squared_error = [0.0 for x in range(LEN_NAMES_MSE * 3)]

pixel_count = 0
for x in range(galaxy_details[0].dimension_x):
    for y in range(galaxy_details[0].dimension_y):
        if array01[x][y][0][0] is not None and array01[x][y][0][1] is not None:
            pixel_count += 1
        for z in range(LEN_NAMES_AE):
            if array01[x][y][z][0] is not None and array01[x][y][z][1] is not None:
                if array01[x][y][z][0] != array01[x][y][z][1]:
                    absolute_error[z] += 1
        for z in range(LEN_NAMES_AE, LEN_NAMES_AE + (LEN_NAMES_MSE *3)):
            if array01[x][y][z][0] is not None and array01[x][y][z][1] is not None:
                if array01[x][y][z][0] != array01[x][y][z][1]:
                     mean_squared_error[z - LEN_NAMES_AE] += math.pow(array01[x][y][z][0] - array01[x][y][z][1], 2)

LOG.info('''
Galaxy {0} vs {1}
Different i_sfh = {2} i_ir = {3}
Pixel Count = {4}

Absolute Error
i_sfh = {5:.2f}%
i_ir  = {6:.2f}%

Mean Squared Error
fmu_sfh = {7:10.2f} {15:10.2f} {16:10.2f}
fmu_ir  = {8:10.2f} {17:10.2f} {18:10.2f}
mu      = {9:10.2f} {19:10.2f} {20:10.2f}
s_sfr   = {10:10.2f} {21:10.2f} {22:10.2f}
m       = {11:10.2f} {23:10.2f} {24:10.2f}
ldust   = {12:10.2f} {25:10.2f} {26:10.2f}
mdust   = {13:10.2f} {27:10.2f} {28:10.2f}
sfr     = {14:10.2f} {29:10.2f} {30:10.2f}
'''.format(galaxy_details[0].name,                      # 00
    galaxy_details[1].name,                             # 01
    absolute_error[0],                                  # 02
    absolute_error[1],                                  # 03
    pixel_count,                                        # 04
    absolute_error[0] * 100.0 / pixel_count,            # 05
    absolute_error[1] * 100.0 / pixel_count,            # 06
    mean_squared_error[0] / pixel_count,                # 07
    mean_squared_error[1] / pixel_count,                # 08
    mean_squared_error[2] / pixel_count,                # 09
    mean_squared_error[3] / pixel_count,                # 10
    mean_squared_error[4] / pixel_count,                # 11
    mean_squared_error[5] / pixel_count,                # 12
    mean_squared_error[6] / pixel_count,                # 13
    mean_squared_error[7] / pixel_count,                # 14
    mean_squared_error[8] / pixel_count,                # 15
    mean_squared_error[9] / pixel_count,                # 16
    mean_squared_error[10] / pixel_count,               # 17
    mean_squared_error[11] / pixel_count,               # 18
    mean_squared_error[12] / pixel_count,               # 19
    mean_squared_error[13] / pixel_count,               # 20
    mean_squared_error[14] / pixel_count,               # 21
    mean_squared_error[15] / pixel_count,               # 22
    mean_squared_error[16] / pixel_count,               # 23
    mean_squared_error[17] / pixel_count,               # 24
    mean_squared_error[18] / pixel_count,               # 25
    mean_squared_error[19] / pixel_count,               # 26
    mean_squared_error[20] / pixel_count,               # 27
    mean_squared_error[21] / pixel_count,               # 28
    mean_squared_error[22] / pixel_count,               # 29
    mean_squared_error[23] / pixel_count,               # 30
))