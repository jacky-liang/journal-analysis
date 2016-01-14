from pickle import dump, load

class EntriesDataObject:

    def __init__(self, name, data):
        self.name = name
        self.data = data
        
    def save(self):
        file = open(EntriesDataObject._get_file_name(self.name), 'w')
        dump(self, file)
        file.close()
        
    @staticmethod
    def _get_file_name(name):
        return name + ".edo" if not name.endswith(".edo") else name
        
    @staticmethod
    def load(name):
        file = open(EntriesDataObject._get_file_name(name), 'r')
        obj = load(file)
        file.close()
        return obj