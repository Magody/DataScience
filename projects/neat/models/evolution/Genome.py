import random
from ..data_structures.RandomHashSet import RandomHashSet
from ..nodes.NodeGene import *
from ..nodes.Node import *

class Genome:
    C1:float = 1
    C2:float = 1
    C3:float = 1
    CP:float = 4

    input_nodes:list = [] # type: Node
    hidden_nodes:list = [] # type: Node
    output_nodes:list = [] # type: Node

    score:float = 0

    id_specie: int = -1

    connections:RandomHashSet = None  # ConnectionGene type
    nodes:RandomHashSet = None # NodeGene type

    def __init__(self,nodes,C1=1,C2=1,C3=1,CP=4):

        self.id_specie = -1

        self.C1:float = C1
        self.C2:float = C2
        self.C3:float = C3
        self.CP:float = CP

        self.connections = RandomHashSet()
        self.nodes = RandomHashSet()

        self.score:float = 0

        self.input_nodes:list = [] # type: Node
        self.hidden_nodes:list = [] # type: Node
        self.output_nodes:list = [] # type: Node

        nodeHashMap = dict() # HashMap<Integer, Node>
        for i in range(len(nodes.data)):
            n:NodeGene = nodes.data[i]
            node:Node = Node(n.x)

            nodeHashMap[n.innovation_number] = node

            if n.x <= 0.1:
                self.input_nodes.append(node)
            elif n.x >= 0.9:
                self.output_nodes.append(node)
            else:
                self.hidden_nodes.append(node)

        self.hidden_nodes.sort(key=lambda nod: nod.x, reverse=True)

        # todo: where goes this code?
        for i in range(len(self.connections.data)):
            c:ConnectionGene = self.connections.data[i]
            from_gene:NodeGene = c.from_gene
            to_gene:NodeGene = c.to_gene

            from_node:Node = nodeHashMap[from_gene.innovation_number]
            to_node:Node = nodeHashMap[to_gene.innovation_number]

            con:Connection = Connection(from_node,to_node)
            con.weight = c.weight
            con.enabled = c.enabled

            to_node.connections.append(con)


    """
    calculated the distance between this genome g1 and a second genome g2
        - g1 must have the highest innovation number!
    """
    def distance(self, g2)->float:
        # g2 -> Genome
        g1 = self

        highest_innovation_gene1 = 0
        if g1.connections.size() != 0:
            highest_innovation_gene1 = g1.connections.get(g1.connections.size()-1).innovation_number

        highest_innovation_gene2 = 0
        if g2.connections.size() != 0:
            highest_innovation_gene2 = g2.connections.get(g2.connections.size()-1).innovation_number

        if highest_innovation_gene1 < highest_innovation_gene2:
            g = g1
            g1 = g2
            g2 = g


        index_g1:int = 0
        index_g2:int = 0
        disjoint:int = 0
        excess:int = 0
        weight_diff:float = 0
        similar:int = 0

        while index_g1 < g1.connections.size() and index_g2 < g2.connections.size():
            gene1:ConnectionGene = g1.connections.get(index_g1)
            gene2:ConnectionGene = g2.connections.get(index_g2)

            in1:int = gene1.innovation_number
            in2:int = gene2.innovation_number

            if in1 == in2:
                # similar gene
                similar += 1
                weight_diff += abs(gene1.weight-gene2.weight)
                index_g1 += 1
                index_g2 += 1
            elif in1 > in2:
                # disjoint gene of b
                disjoint += 1
                index_g2 += 1
            else:
                # disjoint gene of a
                disjoint += 1
                index_g1 += 1

        weight_diff /= max(1,similar)
        excess = g1.connections.size() - index_g1

        N = max(g1.connections.size(),g2.connections.size())
        if N < 20:
            N = 1

        return ((self.C1 * disjoint)/N) + ((self.C2 * excess) / N) + (self.C3 * weight_diff)


    def mutateWeightShift(self, WEIGHT_SHIFT_STRENGTH): 
        con:ConnectionGene = self.connections.randomElement()
        if not con is None:
            con.weight = con.weight + ((random.random()*2-1) * WEIGHT_SHIFT_STRENGTH)
        
    def mutateWeightRandom(self, WEIGHT_RANDOM_STRENGTH): 
        con:ConnectionGene = self.connections.randomElement()
        if not con is None:
            con.weight = ((random.random()*2-1) * WEIGHT_RANDOM_STRENGTH)
        
    def mutateLinkToggle(self):
        con:ConnectionGene = self.connections.randomElement()
        if not con is None:
            con.enabled = not con.enabled

    def calculate(self,input:list)->list:
        # input double
        if len(input) != len(self.input_nodes):
            print("DEBUG",len(input), len(self.input_nodes))
            raise Exception("Data doesn't fit")
        
        for i in range(len(self.input_nodes)):
            self.input_nodes[i].output = input[i]

        for n in self.hidden_nodes:
            n.calculate()

        output:list = [0 for _ in range(len(self.output_nodes))]

        for i in range(len(self.output_nodes)):
            self.output_nodes[i].calculate()
            output[i] = self.output_nodes[i].output

        return output


    
    """
    * creates a new genome.
     * g1 should have the higher score
     *  - take all the genes of a
     *  - if there is a genome in a that is also in b, choose randomly
     *  - do not take disjoint genes of b
     *  - take excess genes of a if they exist
     return Genome
    """
    @staticmethod
    def crossover(g1, g2, genome):
        # genome is a "empty" base genome with existing or no nodes

        index_g1 = 0
        index_g2 = 0

        while index_g1 < g1.connections.size() and index_g2 < g2.connections.size():

            gene1:ConnectionGene = g1.connections.get(index_g1)
            gene2:ConnectionGene = g2.connections.get(index_g2)

            in1:int = gene1.innovation_number
            in2:int = gene2.innovation_number

            if in1 == in2:
                # similar gene
                if random.random() > 0.5:
                    genome.connections.add(ConnectionGene.getConnectionStatic(gene1))
                else:
                    genome.connections.add(ConnectionGene.getConnectionStatic(gene2))
                index_g1 += 1
                index_g2 += 1
            elif in1 > in2:
                # disjoint gene of b
                # genome.connections.add(ConnectionGene.getConnectionStatic(gene2))
                index_g2 += 1
            else:
                # disjoint gene of a
                genome.connections.add(ConnectionGene.getConnectionStatic(gene1))
                index_g1 += 1

        
        while index_g1 < g1.connections.size():
            gene1:ConnectionGene = g1.connections.get(index_g1)
            genome.connections.add(ConnectionGene.getConnectionStatic(gene1))
            index_g1 += 1

        for c in genome.connections.data:
            genome.nodes.add(c.from_gene) 
            genome.nodes.add(c.to_gene) 

        return genome
        
