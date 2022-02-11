import random
from ..nodes.NodeGene import Gene 

# data structures
class RandomHashSet:
    hashSet = set() # <T>
    data = []  # <T>

    def __init__(self):
        self.hashSet = set()
        self.data = []

    def contains(self, object)->bool:
        return object in self.hashSet

    def randomElement(self):
        len_hash = self.size()
        if len_hash > 0:
            return self.data[random.randint(0,len_hash-1)]
        return None

    def size(self):
        return len(self.data)

    def add(self,object):
        if object not in self.hashSet:
            self.hashSet.add(object)
            self.data.append(object)
    
    def addSorted(self,object:Gene):

        for i in range(self.size()):
            gene:Gene = self.data[i]
            innovation = gene.innovation_number
            if object.innovation_number < innovation:
                self.hashSet.add(object)
                self.data.insert(i,object)
                return


        self.hashSet.add(object)
        self.data.append(object)

    def clear(self):
        self.hashSet.clear()
        self.data.clear()

    def get(self,index:int):
        if index < 0 or index >= self.size():
            return None
        return self.data[index]
        
    def removeByIndex(self,index:int):
        if index < 0 or index >= self.size():
            return None
        self.hashSet.remove(self.data[index])
        self.data.pop(index)
        
    def remove(self,object):
        self.hashSet.remove(object)
        self.data.remove(object)