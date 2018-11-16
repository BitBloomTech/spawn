import inspect

from multiwindcalc.util.validation import validate_type

class ValueProxy:
    def evaluate(self):
        return NotImplementedError()


class Macro(ValueProxy):
    def __init__(self, value):
        self._value = value

    def evaluate(self):
        return self._value

def evaluate(value_proxy, *args, **kwargs):
    validate_type(value_proxy, ValueProxy, 'value_proxy')
    parameters = inspect.signature(value_proxy.evaluate).parameters
    if 'kwargs' in parameters:
        return value_proxy.evaluate(*args, **kwargs)
    else:
        return value_proxy.evaluate(*args)
