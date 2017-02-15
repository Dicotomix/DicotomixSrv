class interval:
    def __init__(self,a,b):
        self.beg = float(a)
        self.end = float(b)
    def mid(self):
        return (self.beg+self.end)/2.0
    def left(self,other_mid=-1):
        the_mid=self.mid()
        if other_mid != -1:
            the_mid = other_mid
        return interval(self.beg,the_mid)
    def right(self,other_mid=-1):
        the_mid=self.mid()
        if other_mid != -1:
            the_mid = other_mid
        return interval(the_mid,self.end)
    def is_included(self,b):
        return b.beg <= self.beg and b.end >= self.end
    def __str__(self):
        return str((self.beg,self.end))