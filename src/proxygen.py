# Copyright (c) 2024, Austin Brooks <ab.proxygen@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
import subprocess
import argparse
import sys


def build_utvideo_command(ffmpeg: str, input_file: Path, output_file: Path, short_edge: int) -> list[str]:
    # fmt: off
    return \
    [
        ffmpeg,
        "-i", str(input_file),
        "-filter:v",
        (
            "zscale="
                f"w=if(gt(iw\\,ih)\\,-1\\,{short_edge}):"
                f"h=if(gt(iw\\,ih)\\,{short_edge}\\,-1):"
                "filter=spline36:"
                "dither=error_diffusion,"
            "format=yuv422p"
        ),
        "-c:V", "utvideo",
        "-c:a", "pcm_f32le",
        "-f", "matroska",
        "-y",
        str(output_file)
    ]
    # fmt: on


def dir_walker(source_dir: Path, target_dir: Path, ffmpeg_file: str) -> None:
    for item in source_dir.iterdir():
        source_path = source_dir / item.name
        target_path = target_dir / item.name

        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            dir_walker(source_path, target_path, ffmpeg_file)
            continue

        command = build_utvideo_command(ffmpeg_file, source_path, target_path, 540)
        print(command)
        subprocess.run(command)


def main() -> int:
    """Where things get real."""

    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir")
    parser.add_argument("target_dir")
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    target_dir = Path(args.target_dir).resolve()

    target_dir.mkdir(parents=True, exist_ok=True)
    dir_walker(source_dir, target_dir, "ffmpeg")

    return 0


if __name__ == "__main__":
    sys.exit(main())
