# Copyright (c) 2023 Austin Brooks
#
# This file is part of Proxygen.
#
# Proxygen is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Proxygen is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Proxygen. If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys

import const
import config
import core


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'{const.PROGRAM_NAME}: Optimize media files and create proxies')
    parser.add_argument('-v', '--version', action='store_true', help='Display the program version number and exit')
    parser.add_argument('-c', '--config', help='Path to the project configuration file (optional)')
    parser.add_argument('-r', '--refresh', action='store_true', help='Scan files and process any changes')
    args = parser.parse_args()

    if args.version:
        print(const.PROGRAM_NAME, const.PROGRAM_VERSION)
        print("Config file version:", const.CONFIG_VERSION)
        sys.exit(0)

    cfg = config.Config(args.config)
    pxg = core.Core(cfg)

    if args.refresh:
        pxg.refresh()
        sys.exit(0)
