import os
import os.path as path


class DirectoryHandler:
    def __init__(self, base_folder, extension_path=''):
        self._base_folder = base_folder
        self._extension_path = extension_path
        self._digit = 0
        self._relative_path = None
        self._abspath = None

    def make_new_dir(self):
        self._digit += 1
        self._relative_path = path.join(self._extension_path, str(self._digit))\
            if self._extension_path else str(self._digit)
        self._abspath = path.join(self._base_folder, self._relative_path)
        self._prepare_directory()
        return self._relative_path

    @property
    def relative_path(self):
        return self._relative_path

    @property
    def abspath(self):
        return self._abspath

    def _prepare_directory(self):
        try:
            os.makedirs(self._abspath)
        except FileExistsError:
            pass
