from datetime import datetime
from os import listdir
from re import search, compile
from Entry import Entry

class EntryParser:

    P_DATE = compile("Creation Date</key>[\S\s]*?<date>(.*?)</date>")
    P_DATA = compile("Entry Text</key>[\S\s].*?<string>([\S\s]*?)</string>")
    P_ID = compile("UUID</key>[\S\s]*?<string>(.*?)</string>")

    @staticmethod
    def _str_to_datetime(s):
        year = int(s[:4])
        month = int(s[5:7])
        day = int(s[8:10])
        hour = int(s[11:13])
        minute = int(s[14:16])
        second = int(s[17:19])
        return datetime(year, month, day, hour, minute, second)        

    @staticmethod
    def parse_single(path):
        with open(path, 'r') as file:
            raw = file.read()
            date = EntryParser._str_to_datetime(search(EntryParser.P_DATE, raw).group(1))
            data = search(EntryParser.P_DATA, raw).group(1)
            id = search(EntryParser.P_ID, raw).group(1)
            return Entry(id, date, data)
        
    @staticmethod
    def parse_directory(path):
        if not path.endswith('/'):
            path += '/'
        files = listdir(path)
        return [EntryParser.parse_single(path + file) for file in files]