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

import json
import subprocess as sp
import re

from pathlib import Path


NAME = "Proxygen"
VERSION = "0.1.0"


class Core:
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


    def _validate_config_paths(self) -> None:
        # TODO: Check for all required paths specified.
        for k, v in self._config['paths'].items():
            if not v:
                raise FileNotFoundError(f"No path specified for config key: {k}")

            v_path = Path(v)
            if v_path.exists():
                if not v_path.is_dir():
                    raise ValueError(f"Config key points to file instead of directory: {k} -> {v}")
            else:
                v_path.mkdir(parents=True)

            self._config['paths'][k] = v_path


    def __init__(self, config_file: Path) -> None:
        self._config_file = config_file

        with open(config_file, "r", encoding="utf-8") as config_handle:
            self._config = json.load(config_handle)
        self._dict_keys_to_lower_case(self._config)

        self._validate_config_paths()


    def _cache_timeline(self, start_dir: Path, timeline_cache: set) -> None:
        for item_path in start_dir.iterdir():
            if item_path.is_dir():
                self._cache_timeline(item_path, timeline_cache)
            else:
                timeline_cache.add(item_path)


    def _transcode(self, input_file: Path, output_file: Path) -> None:
        if output_file.exists():
            return

        # fmt: off
        command = [
            "ffmpeg",
            "-i", str(input_file),
            "-filter:v", "format=yuv420p",
            "-colorspace", "bt709",
            "-codec:v", "libsvtav1",
            "-g", "4",
            "-bf", "0",
            "-crf", "24",
            "-preset", "10",
            "-svtav1-params",
                "tune=0:" +
                "film-grain-denoise=0:" +
                "film-grain=0:" +
                "fast-decode=0:" +
                "tile-columns=1",
            "-codec:a", "libopus",
            "-b:a", "192k",
            "-f", "matroska",
            "-y",
            str(output_file)
        ]
        # fmt: on

        frame_re = r"^frame=\s*(\d+)\s*fps="
        proc = sp.Popen(command, stderr=sp.STDOUT, stdout=sp.PIPE, text=True, encoding="utf-8", bufsize=1)
        # TODO: wrap with exception catch
        for line in proc.stdout:
        #for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            # TODO: py3.11 walrus operator
            print(line)
            match = re.match(frame_re, line)
            if match:
                print(" ---> ", match.group(1))


    def _refresh_walk(self, original_dir: Path, timeline_dir: Path, timeline_cache: set) -> None:
        for original_item_path in sorted(original_dir.iterdir()):
            timeline_item_path = timeline_dir / original_item_path.name

            if original_item_path.is_dir():
                timeline_item_path.mkdir(parents=True, exist_ok=True)
                self._refresh_walk(original_item_path, timeline_item_path, timeline_cache)
            else:
                self._transcode(original_item_path, timeline_item_path)
                timeline_cache.discard(timeline_item_path)


    def _is_dir_empty(self, dir: Path) -> bool:
        return not next(dir.iterdir(), False)


    def _clean_timeline_walk(self, start_dir: Path) -> None:
        for item_path in start_dir.iterdir():
            if item_path.is_dir():
                self._clean_timeline_walk(item_path)
                if self._is_dir_empty(item_path):
                    item_path.rmdir()


    def _clean_timeline(self, start_dir: Path, timeline_cache: set) -> None:
        for item_path in timeline_cache:
            if item_path.exists():
                if item_path.is_file():
                    item_path.unlink()

        self._clean_timeline_walk(start_dir)


    def refresh(self) -> None:
        timeline_cache = set()
        self._cache_timeline(self._config['paths']['timeline'], timeline_cache)
        self._refresh_walk(self._config['paths']['original'], self._config['paths']['timeline'], timeline_cache)
        self._clean_timeline(self._config['paths']['timeline'], timeline_cache)
