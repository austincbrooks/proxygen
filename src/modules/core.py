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
import threading
import os

import config
import dirprune
import profile
import profile_MLT1


class Core:
    def __init__(self, config: config.Config) -> None:
        self._config = config
        self._timeline_prune = dirprune.DirPrune(config.paths['timeline'])
        self._io_lock = threading.Lock()
        self._profile = profile_MLT1.Profile_MLT1(self._io_lock, config.paths['temp'])


    def _run_job(self, tjob: profile.TranscodeJob) -> None:
        input = tjob.software[0].input_file
        command = tjob.software[0].command_line

        local_time = datetime.now().isoformat(sep=" ", timespec='milliseconds').replace(":", "-")
        log_file = self._config.paths['log'] / f"{local_time} - {str(input.name)}.txt"
        frame_re = r"^frame=\s*(\d+)\s*fps="

        # TODO: wrap with exception catch
        with open(log_file, "w", encoding='utf-8') as log_handle:
            log_handle.write(f"Local time: {local_time}\n")
            log_handle.write("\n")
            log_handle.write("Command line:\n")
            log_handle.writelines("\n".join(command))
            log_handle.write("\n\n")

            proc = sp.Popen(command, stderr=sp.STDOUT, stdout=sp.PIPE, text=True, bufsize=1)
            for line in proc.stdout:
                log_handle.write(line)
                if match := re.match(frame_re, line):
                    print(match.group(1))

        last_access_time = input.stat().st_atime
        last_modify_time = input.stat().st_mtime
        for output_file in tjob.software[0].output_files:
            os.utime(output_file, (last_access_time, last_modify_time))


    def _refresh_recurse(self,
        original_dir: Path,
        timeline_dir: Path
    ) -> None:
        for original_item_path in sorted(original_dir.iterdir()):
            timeline_item_path = timeline_dir / original_item_path.name

            if original_item_path.is_dir():
                timeline_item_path.mkdir(parents=True, exist_ok=True)
                self._refresh_recurse(original_item_path, timeline_item_path)
                continue

            self._timeline_prune.preserve(timeline_item_path)

            if not timeline_item_path.exists():
                tjob = self._profile.transcode(original_item_path, timeline_item_path)
                self._run_job(tjob)


    def refresh(self) -> None:
        paths = self._config.paths

        self._timeline_prune.snapshot()

        self._refresh_recurse(
            paths['original'],
            paths['timeline']
        )

        self._timeline_prune.prune()
