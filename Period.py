class _PeriodType:

    _id = 0

    def __init__(self, name):
        self.name = name
        self.id = _PeriodType._id
        _PeriodType._id += 1
        
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(self.id)
        
    def __str__(self):
        return self.name

class Period:

    YEAR_TYPE = _PeriodType("YEAR")
    MONTH_TYPE = _PeriodType("MONTH")
    DAY_TYPE = _PeriodType("DAY")
    MINUTE_TYPE = _PeriodType("MINUTE")

    def __init__(self, period_type, duration):
        self.period_type = period_type
        self.duration = duration

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.period_type is other.period_type and self.duration is other.duration
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(str(self.period_type) + " " + str(self.duration))
        
    @staticmethod
    def is_greater_than(start, end, period):
        if period.period_type is Period.YEAR_TYPE:
            return end.year - start.year >= period.duration
        elif period.period_type is Period.MONTH_TYPE:
            return end.year - start.year > 0 or end.month - start.month >= period.duration
        elif period.period_type is Period.DAY_TYPE:
            return end.year - start.year > 0 or end.month - start.month != 0 or end.day - start.day >= period.duration
        elif period.period_type is Period.MINUTE_TYPE:
            return end.year - start.year > 0 or end.month - start.month != 0 or end.day - start.day != 0 or end.hour - start.hour != 0 or end.minute - start.minute >= period.duration
        else:
            raise Exception("Unexpected Period Type")