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

from pathlib import Path
import json

import const


class Config:
    def _find_config_file(self, user_specified_path: str = None) -> Path:
        if user_specified_path:
            test_path = Path(user_specified_path)
        else:
            test_path = Path()

        if not test_path.exists():
            msg = "Could not find the config file"
            raise FileNotFoundError(msg)
        
        if test_path.is_dir():
            for test_file in sorted(test_path.iterdir()):
                if test_file.suffix.lower() == ".pxgc":
                    return test_file.resolve()

            msg = "Could not find the config file"
            raise FileNotFoundError(msg)
        else:
            return test_path.resolve()


    def _dict_keys_to_lower_case(self, input: dict) -> None:
        for k, v in input.copy().items():
            k_lower = k.lower()

            if k == k_lower:
                pass
            elif input.get(k_lower):
                del input[k]
                continue
            else:
                input[k_lower] = v
                del input[k]

            if isinstance(v, dict):
                self._dict_keys_to_lower_case(v)


    def _upgrade_config_version_0_to_1(self, config: dict) -> int:
        upgrade_version = 1
        config['versions']['config'] = upgrade_version
        return upgrade_version


    def _upgrade_config_version(self, config: dict) -> None:
        try:
            version = int(config['versions']['config'])
        except Exception:
            msg = "Config file does not have version information"
            raise KeyError(msg)
        
        if version > const.CONFIG_VERSION:
            msg = "Config file version is {config}, but the max supported version is {program}"
            msg = msg.format(config=version, program=const.CONFIG_VERSION)
            raise ValueError(msg)

        try:
            if version == 0:
                version = self._upgrade_config_version_0_to_1(config)
            # An example of how upgrade chaining will work in the future.
            # if version == 1:
            #     version = self._upgrade_config_version_1_to_2(config)
        except Exception:
            msg = "Failed to upgrade the config file from version {v1} to {v2}"
            msg = msg.format(v1=version, v2=version+1)
            raise Exception(msg)


    def _validate_config_paths(self, config: dict) -> None:
        required_paths = set()
        required_paths.add('original')
        required_paths.add('timeline')
        required_paths.add('log')

        paths = {}
        for k, v in config['paths'].items():
            if not v:
                msg = "No path was specified for config file key: {key}"
                msg = msg.format(key=k)
                raise ValueError(msg)

            v_path = Path(v)

            if v_path == v_path.parent:
                msg = "Config file path must not point to root: {key} -> {value}"
                msg = msg.format(key=k, value=v)
                raise ValueError(msg)

            if not v_path.exists():
                v_path.mkdir(parents=True)

            if not v_path.is_dir():
                msg = "Config file path points to a file instead of a directory: {key} -> {value}"
                msg = msg.format(key=k, value=v)
                raise ValueError(msg)

            paths[k] = v_path
            required_paths.discard(k)

        if len(required_paths) > 0:
            msg = "Config file is missing these required paths: {paths}"
            msg = msg.format(paths=", ".join(required_paths))
            raise KeyError(msg)

        self._paths = paths


    def __init__(self, user_specified_path: str = None) -> None:
        config_file = self._find_config_file(user_specified_path)

        with open(config_file, "r", encoding="utf-8") as config_handle:
            config = json.load(config_handle)

        self._dict_keys_to_lower_case(config)
        self._upgrade_config_version(config)
        self._validate_config_paths(config)

        self._config_file = config_file
        self._project_dir = config_file.parent
        self._config = config


    @property
    def config_file(self):
        return self._config_file
    

    @property
    def project_dir(self):
        return self._project_dir


    @property
    def config(self):
        return self._config


    @property
    def paths(self):
        return self._paths
