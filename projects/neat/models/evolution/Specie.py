
from ..data_structures.RandomHashSet import RandomHashSet
from ..evolution.Genome import Genome


# A specie contains one or more genomes
class Specie:
    STATIC_COUNTER = -1

    id:int = -1
    genomes:RandomHashSet = None # type Genome
    representative:Genome = None
    score:float = 0

    def __init__(self,representative:Genome):
        Specie.STATIC_COUNTER += 1

        self.id = int(Specie.STATIC_COUNTER)

        self.genomes = RandomHashSet()
        representative.id_specie = self.id
        self.representative = representative
        self.genomes.add(representative)
        self.score:float = 0

    def put(self, genome:Genome)->bool:
        # put only if correspond to specie
        if genome.distance(self.representative) < self.representative.CP:
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
    
    def reset(self):
        
        self.representative = self.genomes.randomElement()

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.id_specie = -1

        
        self.genomes.clear()
        self.genomes.add(self.representative)
        self.representative.id_species = self.id
        self.score = 0

    def goExtinct(self):

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.id_specie = -1

    def kill(self,percentage:float)->None:
        # ascending

        self.genomes.data.sort(key=lambda genome: genome.score)

        # kill clients with low score
        amount:float = percentage * self.genomes.size()

        i:int = 0
        while i < amount:
            self.genomes.get(0).id_species = -1
            self.genomes.removeByIndex(0)
            i += 1

    def size(self)->int:
        return self.genomes.size()