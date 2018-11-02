

class ValueProxy:
    def evaluate(self):
        return NotImplementedError()


class Macro(ValueProxy):
    def __init__(self, value):
        self._value = value

    def evaluate(self):
        return self._value