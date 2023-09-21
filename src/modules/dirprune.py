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


class DirPrune:
    def _is_dir_empty(self, dir: Path) -> bool:
        return not next(dir.iterdir(), False)


    def _snapshot_recurse(self, start_dir: Path) -> None:
        for item_path in start_dir.iterdir():
            if item_path.is_dir():
                self._snapshot_recurse(item_path)
            else:
                self._snapshot.add(item_path)


    def _prune_recurse(self, start_dir: Path) -> None:
        for item_path in start_dir.iterdir():
            if item_path.is_dir():
                self._prune_recurse(item_path)
                if self._is_dir_empty(item_path):
                    item_path.rmdir()


    def __init__(self, start_dir: any) -> None:
        test_path = Path(start_dir)

        if not test_path.exists():
            msg = "Directory does not exist: {dir}"
            msg = msg.format(dir=str(test_path))
            raise FileNotFoundError(msg)

        if not test_path.is_dir():
            msg = "Path is not a directory: {dir}"
            msg = msg.format(dir=str(test_path))
            raise ValueError(msg)

        if test_path == test_path.root:
            msg = "Pruning cannot be done on a root directory"
            raise ValueError(msg)

        self._start_dir = test_path


    def snapshot(self) -> None:
        self._working_dir = Path.cwd().resolve()
        self._snapshot = set()
        self._snapshot_recurse(self._start_dir)


    def preserve(self, file: Path) -> None:
        self._snapshot.discard(file)


    def prune(self) -> None:
        """
        A check is done to ensure that the working directory
        did not change between the snapshot and the prune.
        If there were any relative paths in the snapshot,
        they would delete the wrong files if the working
        directory changed.
        """
        if Path.cwd().resolve() != self._working_dir:
            msg = "Cannot prune if working directory changes after snapshot"
            raise RuntimeError(msg)

        for item_path in self._snapshot:
            if item_path.exists():
                if item_path.is_file():
                    item_path.unlink()

        self._prune_recurse(self._start_dir)
