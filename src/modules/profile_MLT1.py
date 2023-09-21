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

import profile
from pathlib import Path


class Profile_MLT1(profile.Profile):
    def transcode(self, input_file: Path, output_file: Path) -> profile.TranscodeJob:
        tjob = profile.TranscodeJob()

        # fmt: off
        tcmd = profile.TranscodeCommand()
        tcmd.input_file = input_file
        tcmd.command_line = [
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
        tcmd.output_files.append(output_file)
        tjob.software.append(tcmd)
        # fmt: on

        return tjob
