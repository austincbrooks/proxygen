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

import subprocess as sp
import re

from pathlib import Path
from datetime import datetime

import config
import dirprune


class Core:
    def __init__(self, config: config.Config) -> None:
        self._config = config
        self._timeline_prune = dirprune.DirPrune(config.paths['timeline'])


    def _transcode(self, input_file: Path, output_file: Path, log_file: Path) -> None:
        if output_file.exists():
            return

        # fmt: off
        command = [
            "ffmpeg",
            "-benchmark",
            "-loglevel", "verbose",
            "-i", str(input_file),
            "-filter:v",
                "scale=-2:540,"
                "format=yuv420p",
            "-colorspace", "bt709",
            "-codec:v", "libsvtav1",
            "-g", "4",
            "-bf", "0",
            "-crf", "24",
            "-preset", "10",
            "-svtav1-params",
                "tune=0:"
                "film-grain-denoise=0:"
                "film-grain=0:"
                "fast-decode=0:"
                "tile-columns=1",
            "-codec:a", "libopus",
            "-b:a", "192k",
            "-f", "matroska",
            "-y",
            str(output_file)
        ]
        # fmt: on

        frame_re = r"^frame=\s*(\d+)\s*fps="
        proc = sp.Popen(command, stderr=sp.STDOUT, stdout=sp.PIPE, text=True, bufsize=1)
        # TODO: wrap with exception catch
        with open(log_file, "w", encoding='utf-8') as log_handle:
            log_handle.write("Command line:\n")
            log_handle.writelines("\n".join(command))
            log_handle.write("\n\n")

            for line in proc.stdout:
                log_handle.write(line)
                if match := re.match(frame_re, line):
                    print(match.group(1))


    def _refresh_recurse(self,
        original_dir: Path,
        timeline_dir: Path,
        log_dir: Path
    ) -> None:
        for original_item_path in sorted(original_dir.iterdir()):
            timeline_item_path = timeline_dir / original_item_path.name

            if original_item_path.is_dir():
                timeline_item_path.mkdir(parents=True, exist_ok=True)
                self._refresh_recurse(original_item_path, timeline_item_path, log_dir)
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                log_file = log_dir / f"{timestamp} {original_item_path.stem}.txt"
                self._transcode(original_item_path, timeline_item_path, log_file)
                self._timeline_prune.preserve(timeline_item_path)


    def refresh(self) -> None:
        paths = self._config.paths

        self._timeline_prune.snapshot()

        self._refresh_recurse(
            paths['original'],
            paths['timeline'],
            paths['log']
        )

        self._timeline_prune.prune()
