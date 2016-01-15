from TimeVariantModel import TVM
from EntriesDataObject import EntriesDataObject
from Entry import Entry
from Period import Period
from datetime import datetime
from re import split, compile, IGNORECASE, VERBOSE
from random import random

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

year = Period(Period.YEAR_TYPE, 1)
month = Period(Period.MONTH_TYPE, 1)
day = Period(Period.DAY_TYPE, 1)
minute = Period(Period.MINUTE_TYPE, 1)

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
        
def splitParagraphIntoSentences(paragraph):
    sentenceEnders = compile(r"""
       # Split sentences on whitespace between them.
       (?:               # Group for two positive lookbehinds.
         (?<=[.!?])      # Either an end of sentence punct,
       | (?<=[.!?]['"])  # or end of sentence punct and quote.
       )                 # End group of two positive lookbehinds.
       (?<!  Mr\.   )    # Don't end sentence on "Mr."
       (?<!  Mrs\.  )
       (?<!  Ms\.   )
       (?<!  Jr\.   )
       (?<!  Dr\.   )
       (?<!  Prof\. )
       (?<!  Sr\.   )
       \s+               # Split on whitespace between sentences.
       """,
        IGNORECASE | VERBOSE)
    return sentenceEnders.split(paragraph)
    
def markov_sentences(entry):
    sentences = splitParagraphIntoSentences(entry.data)
    
    sentences_words = []
    for sentence in sentences:
        words = split("\W+", sentence)
        sentences_words.append([word for word in words if len(word) > 0])
        
    result = {}
    for sentence_words in sentences_words:
        for i in range(len(sentence_words) - 1):
            cur, next = sentence_words[i].lower(), sentence_words[i+1].lower()
            if cur in result:
                target_dict = result[cur]
                if next in target_dict:
                    target_dict[next] += 1
                else:
                    target_dict[next] = 1
            else:
                target_dict = {next:1}
                result[cur] = target_dict

    return result
    
result = model.apply(year, markov_sentences)

def make_sentence(dict, size = 10, seed = None):
    n = len(dict)
    if seed is None:
        seed = dict.keys()[int(random() * n)]
        
    def choose_word(word):
        next_words = dict[word]
        total = 0
        for count in next_words.values():
            total += count
        
        selection = random()
        
        bound = 0
        for word, count in next_words.items():
            bound += count / 1.0 / total     
            if bound >= selection:
                return word
        
    cur_word = seed
    sentence = cur_word
    count = 0
    while cur_word in dict and count < size:
        cur_word = choose_word(cur_word)
        sentence += " " + cur_word
        count += 1
    
    return sentence

