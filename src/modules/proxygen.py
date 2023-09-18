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

import multiprocessing as mp
import argparse
import sys
import os

from pathlib import Path

import core


def get_config_file(user_specified_path: str = None) -> Path:
    if user_specified_path:
        test_path = Path(user_specified_path)
    else:
        test_path = Path()

    if not test_path.exists():
        raise FileNotFoundError("Could not find the config file")
    
    if test_path.is_dir():
        for test_file in sorted(test_path.iterdir()):
            if test_file.suffix.lower() == ".pxgc":
                return test_file.resolve()
        raise FileNotFoundError("Could not find the config file")
    else:
        return test_path.resolve()


if __name__ == '__main__':
    # Required to compile Python code to an executable. See:
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    # https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    mp.freeze_support()

    parser = argparse.ArgumentParser(description=f'{core.NAME}: Optimize media files and create proxies')
    parser.add_argument('-v', '--version', action='store_true', help='Display the program version number and exit')
    parser.add_argument('-c', '--config', help='Path to the project configuration file (optional)')
    parser.add_argument('-r', '--refresh', action='store_true', help='Scan files and process any changes')
    args = parser.parse_args()

    if args.version:
        print(core.NAME, core.VERSION)
        sys.exit(0)

    config_file = get_config_file(args.config)
    os.chdir(config_file.parent)
    pxg = core.Core(config_file)

    if args.refresh:
        pxg.refresh()
        sys.exit(0)
