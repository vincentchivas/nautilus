
class Config:

    def __init__(self, map):
        self.data = map

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif 'default' in self.data:
            return self.data['default']
        else:
            return ''
