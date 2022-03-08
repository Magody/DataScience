from ..data_structures.HashSorted import *

class Gene(HashStructure):
    # inherith key
    innovation_number:int = 0
    def __init__(self,innovation_number):
        self.innovation_number = innovation_number