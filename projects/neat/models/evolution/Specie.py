
from ..data_structures.RandomHashSet import RandomHashSet
from ..evolution.Genome import Genome
from ..network.Neuron import *
import random

# A specie contains one or more genomes
class Specie:
    STATIC_COUNTER = -1

    id:int = -1
    genomes:RandomHashSet = None # type Genome
    representative:Genome = None
    score:float = 0

    THRESHOLD_FAIL:int = 5


    def __init__(
        self,
        representative:Genome,
        probability_crossover:float = 0.75, # paper: In each generation, 25% of offspring resulted from mutation without crossover. With 75% we mutate new crossover
        C1=1, # Specie delta disjoint
        C2=1, # Specie delta excess
        C3=1, # 0.4 Specie delta weight # for DPNV, may be better idea to increase this to 3
        specie_threshold=4  # Specie delta threshold
    ):

        Specie.STATIC_COUNTER += 1
        self.id = Specie.STATIC_COUNTER

        self.best_score:float = -math.inf
        self.generations_from_last_improve:int = 0
        self.generations_alive:int = 0

        self.can_reproduce:int = True

        self.C1:float = C1
        self.C2:float = C2
        self.C3:float = C3
        self.specie_threshold:float = specie_threshold

        self.probability_crossover = probability_crossover



        self.genomes = RandomHashSet()
        representative.id_specie = self.id
        self.representative = representative
        self.genomes.add(representative)
        self.score:float = 0

    def __str__(self)->str:
        return f"Specie: {self.id}. Generations from last improve: {self.generations_from_last_improve}. Alive: {self.generations_alive} . Best.: {self.best_score}. Pop.: {self.genomes.size()}. Can: {self.can_reproduce}"
        

    """
    calculated the distance between this genome g1 and a second genome g2
        - g1 must have the highest innovation number!
    """
    def distance(self, g1:Genome, g2:Genome)->float:
        # todo: check this function with the paper

        len_connections_g1:int = len(g1.connections)
        len_connections_g2:int = len(g2.connections)

        highest_innovation_gene1 = 0
        if len_connections_g1 != 0:
            highest_innovation_gene1 = g1.connections[len_connections_g1-1].innovation_number

        highest_innovation_gene2 = 0
        if len_connections_g2 != 0:
            highest_innovation_gene2 = g2.connections[len_connections_g2-1].innovation_number

        if highest_innovation_gene1 < highest_innovation_gene2:
            g = g1
            g1 = g2
            g2 = g
            # recalculate lens
            len_connections_g1:int = len(g1.connections)
            len_connections_g2:int = len(g2.connections)

        index_g1:int = 0
        index_g2:int = 0
        disjoint:int = 0
        excess:int = 0
        weight_diff:float = 0
        similar:int = 0

        while index_g1 < len_connections_g1 and index_g2 < len_connections_g2:
            gene1:Connection = g1.connections[index_g1]
            gene2:Connection = g2.connections[index_g2]

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
        excess = len_connections_g1 - index_g1

        # in the paper genes are connections, the same crossed in crossover
        g1_number_genes = len_connections_g1 # + len(g1.neurons)
        g2_number_genes = len_connections_g2 # + len(g2.neurons)

        # factor N, the number of genes in the larger genome, normalizes for genome size
        N = max(g1_number_genes,g2_number_genes)
        if N < 20:
            # paper recommendation
            N = 1

        factor_disjoint:float = ((self.C1 * disjoint)/N)
        factor_excess:float = ((self.C2 * excess)/N)
        factor_weight:float = (self.C3 * weight_diff)

        return factor_disjoint + factor_excess + factor_weight


    def put(self, genome:Genome)->bool:
        # put only if correspond to specie
        similarity:float = self.distance(genome, self.representative)
        if similarity < self.specie_threshold:
            # it is part of the specie
            genome.id_specie = self.id
            self.genomes.add(genome)
            return True

        return False

    def forcePut(self, genome:Genome)->None:
        genome.id_specie = self.id
        self.genomes.add(genome)

    def evaluateScore(self)->None:
        v:float = 0
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            v += genome.score
        self.score = v/self.genomes.size()

    def increaseGeneration(self)->None:
        self.generations_alive += 1
        if self.score > self.best_score:
            self.generations_from_last_improve = 0
            self.best_score = self.score
            self.can_reproduce = True
        else:
            self.generations_from_last_improve += 1
            if self.generations_from_last_improve >= Specie.THRESHOLD_FAIL:
                self.can_reproduce = False

        

    
    def reset(self):
        
        self.representative = self.genomes.randomElement()

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.id_specie = -1

        
        self.genomes.clear()
        self.genomes.add(self.representative)
        self.representative.id_specie = self.id
        self.score = 0


    def goExtinct(self):

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.id_specie = -1

    def reducePopulation(self,percentage:float)->None:
        # ascending

        self.genomes.data.sort(key=lambda genome: genome.score)

        # kill clients with low score
        amount:float = percentage * self.genomes.size()

        i:int = 0
        while i < amount:
            self.genomes.get(0).id_specie = -1
            self.genomes.get(0).score = 0
            self.genomes.removeByIndex(0)
            i += 1

    def size(self)->int:
        return self.genomes.size()

    def breed(self, genome_container:Genome)->Genome:
        
        p:float = random.random()
        len_genomes:int = self.genomes.size()

        if p < self.probability_crossover:
            # todo: we can control and improve if are the same?
            g1:Genome = self.genomes.get(random.randint(0,len_genomes-1))
            g2:Genome = self.genomes.get(random.randint(0,len_genomes-1))

            if g1.score > g2.score:
                return Genome.crossover(g1,g2,genome_container)
            return Genome.crossover(g2,g1,genome_container)

        return Genome.copy(self.genomes.get(random.randint(0,len_genomes-1)))

   