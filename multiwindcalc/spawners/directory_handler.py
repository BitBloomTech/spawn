import os
from os import path


class DirectoryHandler:
    def __init__(self, base_folder, relative_path=''):
        self._base_folder = path.abspath(base_folder)
        self._relative_path = relative_path
        self._digit = 0
        self._prepare_directory()

    def branch(self, new_dir=None):
        self._digit += 1
        if new_dir is None:
            new_dir = str(self._digit)
        return DirectoryHandler(self._base_folder, path.join(self._relative_path, new_dir))

    @property
    def relative_path(self):
        return self._relative_path

    @property
    def abspath(self):
        return path.join(self._base_folder, self._relative_path)

    def _prepare_directory(self):
        try:
            os.makedirs(self.abspath)
        except FileExistsError:
            pass
