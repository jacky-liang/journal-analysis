from requests import post
from numpy import array, float

class Sentiment:

    _USERNAME = "a2abf138-9fc9-4777-a2c2-97d7f352b9e6"
    _PASSWORD = "R7CIOmJq1bGU"
    _ENDPOINT = "https://gateway.watsonplatform.net/tone-analyzer-experimental/api/v2/tone"
    _HEADERS = {"content-type":"text/plain"}

    def __init__(self, data):
        self._data = data
        self._raw_score = None
        self._score = None
        
    @property
    def text(self):
        return self._data
        
    @property
    def raw_score(self):
        if self._raw_score is None:
            r = post(Sentiment._ENDPOINT, headers = Sentiment._HEADERS, data = self._data, auth = (Sentiment._USERNAME, Sentiment._PASSWORD))
            self._raw_score = r.json()
        return self._raw_score
        
    @staticmethod
    def _parse_raw_score(raw_score):
        '''
        Turns raw_score, a json, into the following 9d vector:
        cheerfulness, negative, anger, analytical, confident, tentative, openness, conscientiousness, agreeableness
        '''
        score = array([None] * 9).astype(float)
        k = 0
        for i in range(3):
            for j in range(3):
                score[k] = raw_score['children'][i]["children"][j]["normalized_score"]
                k += 1
                
        return score
        
    @property
    def score(self):
        if self._score is None:
            self._score = Sentiment._parse_raw_score(self.raw_score)
        return self._score
        
