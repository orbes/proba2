# egy �lt megval�s�t� oszt�ly
# k�t �l ugynaz, ha ugyanazok a nodok a c�l �s startnodejaik
# ((egyik c�lja = m�sik c�lja �s egyik start = m�sik start)
#   vagy (egyik c�l = m�sik start �s egyik start =  m�sik c�l))

class Pair:
    def __init__(self, start, destination):
        self.start = start
        self.destination = destination

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return NotImplemented
        return (self.start == other.start and self.destination == other.destination) or (
                    self.start == other.destination and self.destination == other.start)

    def __repr__(self):
        return str(self.start) + ': ' + self.destination
