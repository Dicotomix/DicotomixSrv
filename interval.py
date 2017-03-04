class interval:
    def __init__(self, a, b):
        self.beg = float(a)
        self.end = float(b)

    def mid(self):
        return (self.beg + self.end) / 2.0

    def length(self):
        return self.end - self.beg

    def leftPart(self, other_mid=-1):
        if other_mid != -1:
            the_mid = other_mid
        else:
            the_mid = self.mid()
        return interval(self.beg, the_mid)

    def rightPart(self, other_mid=-1):
        if other_mid != -1:
            the_mid = other_mid
        else:
            the_mid = self.mid()
        return interval(the_mid, self.end)

    def isIncluded(self,b):
        return b.beg <= self.beg and b.end >= self.end

    def __str__(self):
        return str((self.beg, self.end))