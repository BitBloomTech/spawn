"""Utilities related to string parsing and manipulation
"""
def quote(strpath):
    """Wrap the given string in quotes

    :param strpath: A string representing a path
    :type strpath: str
    """
    if strpath[0] != '"' or strpath[-1] != '"':
        return '"' + strpath + '"'
