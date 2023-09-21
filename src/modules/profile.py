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

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
import threading
import uuid


@dataclass
class TranscodeCommand:
    input_file: Path = None
    command_line: list[str] = field(default_factory=list)
    output_files: list[Path] = field(default_factory=list)
    temp_files: list[Path] = field(default_factory=list)


@dataclass
class TranscodeJob:
    software: list[TranscodeCommand] = field(default_factory=list)
    # nvenc: list[TranscodeCommand] = field(default_factory=list)
    # qsv: list[TranscodeCommand] = field(default_factory=list)
    # amf: list[TranscodeCommand] = field(default_factory=list)
    # vaapi: list[TranscodeCommand] = field(default_factory=list)
    # vulkan: list[TranscodeCommand] = field(default_factory=list)


class Profile(ABC):
    def __init__(self, io_lock: threading.Lock, temp_dir: Path) -> None:
        self._io_lock = io_lock
        self._temp_dir = temp_dir


    def _get_temp_file(self) -> Path:
        try:
            # TODO: Lock needed? This may not be threaded.
            self._io_lock.acquire()

            while True:
                temp_file = self._temp_dir / f"{uuid.uuid4()}.tmp"
                if not temp_file.exists():
                    break

            temp_file.touch(exist_ok=False)
        finally:
            self._io_lock.release()

        return temp_file


    @abstractmethod
    def transcode(self, input_file: Path, output_file: Path) -> TranscodeJob:
        pass
