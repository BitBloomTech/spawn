import re
import string

LETTERS = string.ascii_lowercase

class PathBuilder:
    def __init__(self, path=''):
        self._path = path
    
    def join(self, other):
        new_path = '{}/{}'.format(self._path, other) if self._path else other
        return PathBuilder(new_path)
    
    def join_start(self, other):
        new_path = '{}/{}'.format(other, self._path) if self._path else other
        return PathBuilder(new_path)
    
    def format(self, properties, indices=None):
        if indices is not None:
            if properties.keys() != indices.keys():
                raise ValueError('index must be provided for all properties')
        next_path = self._path
        for key in properties.keys():
            token_regex = self._token(key)
            search_result = re.search(token_regex, next_path)
            if search_result:
                index_format = search_result.group('index_format')
                if index_format:
                    if indices is None:
                        raise ValueError('indices must be provided if index formats are defined')
                    substitution = self.index(indices[key], index_format)
                else:
                    substitution = str(properties[key])
                next_path = next_path.replace(search_result.group(0), substitution)
        remaining_values = re.search(self._token('.*'), next_path)
        if remaining_values:
            raise ValueError('No value supplied for token "{}"'.format(remaining_values.group(0)))
        return PathBuilder(next_path)
    
    @staticmethod
    def _token(value):
        return r'\{' + value + r':?(?P<index_format>[^\}]*)\}' 
    
    def __repr__(self):
        return self._path
    
    @staticmethod
    def index(index, index_format='1'):
        if re.search('0*[\d]+', index_format):
            start_index = int(index_format)
            pad_width = len(index_format)
            return '{index:0>{pad_width}}'.format(index=index + start_index, pad_width=pad_width)
        if re.search('[a]+', index_format):
            index_string = ''
            while index > 0:
                next_value, index = index % 26, index // 26
                index_string = LETTERS[next_value] + index_string
            return '{index_string:a>{pad_width}}'.format(index_string=index_string, pad_width=len(index_format))
        
        raise ValueError('index_format has unsupported value {}'.format(index_format))