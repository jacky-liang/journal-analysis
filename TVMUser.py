from TimeVariantModel import TVM
from EntriesDataObject import EntriesDataObject
from Entry import Entry
from Period import Period
from datetime import datetime
from re import split, compile, IGNORECASE, VERBOSE
from random import random
from numpy import matrix, array, dot
from numpy.linalg import svd, norm

class TVMUser:

    _EPOCH = datetime(2000, 1, 1)

    @staticmethod
    def comparator(entry):
        diff = entry.date - TVMUser._EPOCH
        return diff.days * 24 * 60 * 60 + diff.seconds
    
    @staticmethod
    def combinator(entry1, entry2):
        return Entry(entry1.id, entry1.date, entry1.data + entry2.data)
    
    year = Period(Period.YEAR_TYPE, 1)
    month = Period(Period.MONTH_TYPE, 1)
    day = Period(Period.DAY_TYPE, 1)
    minute = Period(Period.MINUTE_TYPE, 1)
        
    insig_words = ("i", "to", "and", "the", "you", "of", "this", "is", "it", "t", "my", "on", "for", "as", "ll", "s", "a", "that", "in", "be", "not", "was", "with", "me", "have", "are", "your", "or", "can", "when", "our", "all", "but", "how", "did", "which", "what", "there", "just", "its", "has", "been", "from", "one", "her", "she", "were", "had", "more", "about", "they", "their", "his")
        
    def __init__(self, name):
        self.entries = EntriesDataObject.load(name)
        self.model = TVM(self.entries.data, TVMUser.comparator, TVMUser.combinator)
        self.results = {}
    
    def _apply(self, period, name, function):
        if (period, name) not in self.results:
            self.results[(period, name)] = self.model.apply(period, function)
        return self.results[(period, name)]
        
    def get_length(self, period):
        def length(entry):
            return len(entry.data)
        return self._apply(period, "length", length)

    def get_freq(self, period):
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
        return self._apply(period, "freq", freq)

    def print_freq(self, period, i):
        result = self.get_freq(period)[i]
    
        def include(word):
            if word.lower() in TVMUser.insig_words:
                return False
            if len(word) <= 2:
                return False
            return True
            
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
        
    @staticmethod
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
        
    def get_markov_sentences(self, period):
        def markov_sentences(entry):
            sentences = TVMUser.splitParagraphIntoSentences(entry.data)
            
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
        return self._apply(period, "markov_sentences", markov_sentences)
    
    def make_markov_sentences(self, period, i, size=10, seed=None):
        dict = self.get_markov_sentences(period)[i]
        
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

    def make_freq_vectors(self, period):
        results = self.get_freq(period)
        
        word_space_map = {}
        word_space_map_inverse = {}
        i = 0
        for result in results:
            for word, _ in result[1]:
                word = word.lower()
                if word not in word_space_map:
                    word_space_map[word] = i
                    word_space_map_inverse[i] = word
                    i += 1
        n = i + 1
        
        dates = []
        freq_vectors = []
        for result in results:
            dates.append(result[0])
            
            vec = [0 for i in range(n)]
            for word, freq in result[1]:
                vec[word_space_map[word]] = freq
                
            freq_vectors.append(vec)
        
        return dates, freq_vectors, word_space_map_inverse
        
u = TVMUser("all_entries")
dates, freq_vectors, word_space_map_inverse = u.make_freq_vectors(TVMUser.month)

def PCs_to_words(e, U, n, dim_to_word):
    results = []
    for i in range(n):
        PC = U[i]
        words = []
        for i in range(PC.shape[1]):
            val = abs(PC[0, i])
            if abs(val) > e:
                words.append((dim_to_word[i], val))
            words = sorted(words, key = lambda x: x[1])
        results.append(words)
    return results
    
def PCA():
    M = matrix(freq_vectors).T
    U, s, Vt = svd(M)
    p_words = PCs_to_words(0.1, U, 10, word_space_map_inverse)
    for p_word in p_words:
        line = ""
        for word, _ in p_word:
            line += word + " "
        print line
        
fv = [array(v) for v in freq_vectors]
def cos_sim(u, v):
    return dot(u, v) / norm(u) / norm(v)
    