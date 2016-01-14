from TimeVariantModel import TVM
from EntriesDataObject import EntriesDataObject
from Entry import Entry
from Period import Period
from datetime import datetime
from re import split

_EPOCH = datetime(2000, 1, 1)

def comparator(entry):
    diff = entry.date - _EPOCH
    return diff.days * 24 * 60 * 60 + diff.seconds
    
def combinator(entry1, entry2):
    return Entry(entry1.id, entry1.date, entry1.data + entry2.data)

def length(entry):
    return len(entry.data)

def freq(entry):
    all_words = split('\W+', entry.data)
    words = {}
    for word in all_words:
        word = word.lower()
        if word in words:
            words[word] += 1
        else:
            words[word] = 1
    n = len(all_words)
    freqs = []
    for word, count in words.items():
        freqs.append((word, count * 1.0 / n))
    return entry.date, sorted(freqs, key = lambda x: x[1])[::-1], len(entry.data)
    
entries = EntriesDataObject.load("all_entries")
model = TVM(entries.data, comparator, combinator)

month = Period(Period.MONTH_TYPE, 1)
day = Period(Period.DAY_TYPE, 1)
minute = Period(Period.MINUTE_TYPE, 1)
result = model.apply(month, freq)

insig_words = ("i", "to", "and", "the", "you", "of", "this", "is", "it", "t", "my", "on", "for", "as", "ll", "s", "a", "that", "in", "be", "not", "was", "with", "me", "have", "are", "your", "or", "can", "when", "our", "all", "but", "how", "did", "which", "what", "there", "just", "its", "has", "been", "from", "one", "her", "she", "were", "had", "more", "about", "they", "their", "his")

def include(word):
    if word.lower() in insig_words:
        return False
    if len(word) <= 2:
        return False
    return True

def print_freq(result):
    for item in result:
        freq = item[1]
        date = item[0]
        length = item[2]
        s = str(date.year) + " " + str(date.month) + " | " + str(length) + ": "
        i = 0
        for item in freq:
            word = item[0]
            if include(word):
                s += word + ", "
                i += 1
            if i >= 10:
                break
        print s