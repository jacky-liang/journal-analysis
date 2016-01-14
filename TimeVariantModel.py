from Period import Period

class TVM:
    
    def __init__(self, data, comparator, combinator):
        self._data_raw = data
        self._comparator = comparator
        self._combinator = combinator
        
        self._data_raw = sorted(self._data_raw, key = self._comparator)
        self._data_transformed = {}
        
    def _transform(self, period):
        transformed = []
        current_first = self._data_raw[0]
        current = current_first
        for data in self._data_raw[1:]:
            if Period.is_greater_than(current_first.date, data.date, period):
                transformed.append(current)
                current = data
                current_first = data
            else:
                current = self._combinator(current, data)
        transformed.append(current)
        return transformed
        
    def apply(self, period, function):
        if period not in self._data_transformed:
            self._data_transformed[period] = self._transform(period)
        return [function(data) for data in self._data_transformed[period]]