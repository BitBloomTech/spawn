from abc import abstractmethod


class InputEditor:
    @abstractmethod
    def write(self, file_path, editions):
        pass
