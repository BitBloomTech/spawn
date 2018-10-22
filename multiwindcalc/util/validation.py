from os import path

def validate_type(value, expected, name):
    """Validates that the value is of the expected type. Raises ``TypeError`` if not.
    
    Parameters
    ----------
    value : obj
        Value to validate
    expected : type
        The expected type
    name : str
        The name of the value
    """
    if not isinstance(value, expected):
        raise TypeError('{} must be of type {}; was {}'.format(name, expected.__name__, type(value).__name__))

def validate_file(value, name):
    """Validates that the given file exists and is accessible. Raises ``FileNotFoundError`` if not.

    Parameters
    ----------
    value : str or path-like
        Path to the file to validate
    name : str
        The name of the value
    """
    if not path.isfile(value):
        raise FileNotFoundError('File {} not found or not accessible at {}'.format(name, value))
