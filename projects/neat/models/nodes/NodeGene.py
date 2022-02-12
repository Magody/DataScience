import math

class Gene:
    innovation_number:int = 0
    def __init__(self,innovation_number):
        self.innovation_number = innovation_number

class NodeGene(Gene):
    # Allow connections from low x value to high y value
    x = 0
    y = 0
    def __init__(self,innovation_number):
        super().__init__(innovation_number)
        self.x = 0
        self.y = 0

    def equals(self, object):
        if not type(object) is Gene:
            return False
        
        return self.innovation_number == object.innovation_number

    def __str__(self):
        return f"(NodeGene: {self.innovation_number})"

    def hashCode(self):
        return self.innovation_number
    
class ConnectionGene(Gene):
    from_gene:NodeGene = None
    to_gene:NodeGene = None

    weight:float = 0
    enabled:bool = True

    replace_index:int = 0

    def __init__(self,from_gene:NodeGene,to_gene:NodeGene):
        self.from_gene = from_gene
        self.to_gene = to_gene
        self.weight:float = 0
        self.enabled:bool = True
        self.replace_index:int = 0

    def equals(self, object):
        if not type(object) is ConnectionGene:
            return False
        
        return self.from_gene.equals(object.from_gene) and self.to_gene.equals(object.to_gene)

    def __str__(self):
        return f"(ConnectionGene: from={self.from_gene.innovation_number},to={self.to_gene.innovation_number},weight={self.weight},enabled={self.enabled},innovation_number={self.innovation_number})"

    def hashCode(self)->int:
        MAX_NODES = math.pow(2,20)
        return int(self.from_gene.innovation_number * MAX_NODES + self.to_gene.innovation_number)
    
    @staticmethod
    def getConnectionStatic(con):
        """
        ARG ConnectionGene
        Return ConnectionGene
        """
        c:ConnectionGene = ConnectionGene(con.from_gene,con.to_gene)
        c.innovation_number = con.innovation_number
        c.weight = con.weight
        c.enabled = con.enabled
        return c