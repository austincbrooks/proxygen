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
import platform
import shutil
import subprocess
import argparse
import sys


def find_self_dir() -> Path:
    """Returns the directory where the running executable is stored."""

    if getattr(sys, "frozen", False):
        # Compressed executable, unpacked in /tmp.
        self_dir = Path(sys.executable).parent.resolve()
    else:
        try:
            # Non-interactive script runner.
            self_dir = Path(__file__).parent.resolve()
        except NameError:
            # Interactive command window.
            self_dir = Path.cwd().resolve()

    # Parent of "bin/*.exe" or "src/*.py" is the same place.
    if (self_dir.parent / "PROXYGEN.root").exists():
        return self_dir

    raise FileNotFoundError("Cannot find Proxygen root directory")


def find_ffmpeg_exe() -> str:
    if platform.system() == "Windows":
        ffmpeg_exe = "ffmpeg.exe"
    else:
        ffmpeg_exe = "ffmpeg"

    self_dir = find_self_dir()
    print("self_dir:", self_dir)

    # Same-directory ffmpeg should always take precedence.
    probe_file = (self_dir / ffmpeg_exe).resolve()
    print("probe_file", probe_file)
    if probe_file.exists():
        return str(probe_file)

    # For running .py source code out of a portable archive.
    probe_file = (self_dir.parent / "bin" / ffmpeg_exe).resolve()
    print("probe_file", probe_file)
    if probe_file.exists():
        return str(probe_file)

    # For running .py source code out of a local dev repo.
    probe_file = (self_dir.parent / "dist" / ffmpeg_exe).resolve()
    print("probe_file", probe_file)
    if probe_file.exists():
        return str(probe_file)

    # Hunt for a system-wide ffmpeg in PATH.
    probe_file = shutil.which(ffmpeg_exe)
    print("probe_file", probe_file)
    if probe_file is not None:
        return probe_file

    raise FileNotFoundError("Cannot find FFmpeg executable")


def build_utvideo_command(ffmpeg_exe: str, input_file: Path, output_file: Path, short_edge: int) -> list[str]:
    # fmt: off
    return \
    [
        ffmpeg_exe,
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


def dir_walker(source_dir: Path, target_dir: Path, ffmpeg_exe: str) -> None:
    for item in source_dir.iterdir():
        source_path = source_dir / item.name
        target_path = target_dir / item.name

        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            dir_walker(source_path, target_path, ffmpeg_exe)
            continue

        command = build_utvideo_command(ffmpeg_exe, source_path, target_path, 540)
        print(command)
        subprocess.run(command)


def main() -> int:
    """Where things get real."""

    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir")
    parser.add_argument("target_dir")
    args = parser.parse_args()

    ffmpeg_exe = find_ffmpeg_exe()
    source_dir = Path(args.source_dir).resolve()
    target_dir = Path(args.target_dir).resolve()

    target_dir.mkdir(parents=True, exist_ok=True)
    dir_walker(source_dir, target_dir, ffmpeg_exe)

    return 0


if __name__ == "__main__":
    sys.exit(main())
