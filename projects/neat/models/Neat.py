import random

from sympy import C
from .data_structures.RandomHashSet import RandomHashSet
from .data_structures.RandomSelector import RandomSelector
from .evolution.Genome import Genome
from .nodes.NodeGene import *
from .evolution.Specie import Specie



class Neat:

    

    SURVIVORS:float = 0.8


    WEIGHT_SHIFT_STRENGTH:float = 0.3
    WEIGHT_RANDOM_STRENGTH:float = 1

    PROBABILITY_MUTATE_LINK:float = 0.01
    PROBABILITY_MUTATE_NODE:float = 0.1
    PROBABILITY_MUTATE_WEIGHT_SHIFT:float = 0.02
    PROBABILITY_MUTATE_WEIGHT_RANDOM:float = 0.02
    PROBABILITY_MUTATE_TOGGLE_LINK:float = 0
    

    all_connections = dict() # type hashmap<ConnectionGene, ConnectionGene>

    all_nodes:RandomHashSet = None # type NodeGene
    genomes:RandomHashSet = None # type Genome
    species:RandomHashSet = None # type Specie

    max_clients:int = 0
    output_size:int = 0
    input_size:int = 0



    def __init__(self,input_size:int, output_size:int, clients:int):
        

        

        self.SURVIVORS:float = 0.8

        
        self.all_connections = dict()
        self.all_nodes = RandomHashSet()
        self.genomes = RandomHashSet()
        self.species = RandomHashSet()


        self.WEIGHT_SHIFT_STRENGTH:float = 0.3
        self.WEIGHT_RANDOM_STRENGTH:float = 1
        self.PROBABILITY_MUTATE_LINK:float = 0.01
        self.PROBABILITY_MUTATE_NODE:float = 0.0003
        self.PROBABILITY_MUTATE_WEIGHT_SHIFT:float = 0.02
        self.PROBABILITY_MUTATE_WEIGHT_RANDOM:float = 0.02
        self.PROBABILITY_MUTATE_TOGGLE_LINK:float = 0

        self.reset(input_size, output_size, clients)


    def reset(self, input_size:int, output_size:int, clients:int)->None:
        # print("d:NEAT:reset")
        self.input_size = input_size
        self.output_size = output_size
        self.max_clients = clients

        self.all_connections.clear()
        self.all_nodes.clear()
        self.genomes.clear()

        for i in range(input_size):
            n:NodeGene = self.getNodeCommon()
            n.x = 0.1
            n.y = (i+1)/float(input_size+1)

        for i in range(output_size):
            n:NodeGene = self.getNodeCommon()
            n.x = 0.9
            n.y = (i+1)/float(output_size+1)

        for i in range(self.max_clients):
            genome:Genome = self.empty_genome()
            self.genomes.add(genome)
    

    def getConnection(self, node1:NodeGene, node2:NodeGene)->ConnectionGene:

        connectionGene:ConnectionGene = ConnectionGene(node1,node2)

        key = connectionGene.hashCode()
        if key in self.all_connections:
            # todo: check that hashcode is the key
            connectionGene.innovation_number = self.all_connections[key].innovation_number
        else:
            connectionGene.innovation_number = len(self.all_connections) + 1
            self.all_connections[key] = connectionGene
        
        return connectionGene

    def setReplaceIndex(self, node1:NodeGene, node2:NodeGene, index:int)->None:
        connectionGene:ConnectionGene = ConnectionGene(node1,node2)
        key = connectionGene.hashCode()
        self.all_connections[key].replace_index = index


    def getReplaceIndex(self, node1:NodeGene, node2:NodeGene)->None:
        connectionGene:ConnectionGene = ConnectionGene(node1,node2)
        key = connectionGene.hashCode()
        data:ConnectionGene = self.all_connections.get(key, None)

        if data is None:
            return 0
        return data.replace_index

    def getNodeCommon(self)->NodeGene:
        n:NodeGene = NodeGene(self.all_nodes.size()+1)
        self.all_nodes.add(n)
        return n

    def getNode(self,id:int)->NodeGene:
        if id <= self.all_nodes.size():
            return self.all_nodes.get(id-1)
        return self.getNodeCommon()

    
    def empty_genome(self) -> Genome:

        g:Genome = Genome()
        for i in range(self.input_size+self.output_size):
            g.nodes.add(self.getNode(i+1))

        return g

    
    # We need the reference control, so this method can't be in Specie
    def breedFromSpecie(self, specieFrom:Specie)->Genome:
        # return Genome
        genome1:Genome = specieFrom.genomes.randomElement()
        genome2:Genome = specieFrom.genomes.randomElement()

        genome_base:Genome = self.empty_genome()
        
        if genome1.score > genome2.score:
            return Genome.crossover(genome1,genome2,genome_base)
        
        return Genome.crossover(genome2,genome1,genome_base)


    def check(self,max_data=11)->bool:
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            if genome.nodes.size() > max_data:
                return genome.nodes
        return None

    def evolve(self)->None:

        self.genSpecies()
        self.kill()
        self.removeExtinctSpecies()
        self.reproduce()
        self.mutate()

        nods = self.check(11)
        if not nods is None:
            print("Error", nods.size())

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.id_specie = -1


    def printSpecies(self)->None:
        print("##########################################")
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            print(f"{s} {s.score} {s.size()}")
        
    def reproduce(self)->None:

        selector:RandomSelector = RandomSelector() # type Species

        # Get species with their score
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            selector.add(s,s.score)
        
        
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            # if the specie is dead select a random
            if genome.id_specie == -1:
                s:Specie = selector.random()
                # break new genome
                self.genomes.data[i] = self.breedFromSpecie(s)
                # force this client into the specie
                s.forcePut(self.genomes.data[i])
                

    def mutate(self)->None:

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            if random.random() < self.PROBABILITY_MUTATE_LINK:
                self.mutateGenomeLink(genome)
            if random.random() < self.PROBABILITY_MUTATE_NODE:
                self.mutateGenomeNode(genome)
            if random.random() < self.PROBABILITY_MUTATE_WEIGHT_SHIFT:
                genome.mutateWeightShift(self.WEIGHT_SHIFT_STRENGTH)
            if random.random() < self.PROBABILITY_MUTATE_WEIGHT_RANDOM:
                genome.mutateWeightRandom(self.WEIGHT_RANDOM_STRENGTH)
            if random.random() < self.PROBABILITY_MUTATE_TOGGLE_LINK:
                genome.mutateLinkToggle()

    def mutateGenomeLink(self, genome:Genome, trysearch=100):

        for i in range(trysearch):
            a:NodeGene = genome.nodes.randomElement()
            b:NodeGene = genome.nodes.randomElement()

            if a is None or b is None:
                continue

            con:ConnectionGene = None
            if a.x < b.x:
                con = ConnectionGene(a,b)
            else:
                con = ConnectionGene(b,a)

            if genome.connections.contains(con):
                continue

            con = self.getConnection(con.from_gene, con.to_gene)
            con.weight = (random.random() * 2 - 1) * self.WEIGHT_RANDOM_STRENGTH

            genome.connections.addSorted(con) # check if is connections from genome or neat
            return

    def mutateGenomeNode(self, genome:Genome):
        con:ConnectionGene = genome.connections.randomElement()
        if con is None:
            return

        from_gene:NodeGene = con.from_gene
        to_gene:NodeGene = con.to_gene

        replace_index:int = self.getReplaceIndex(from_gene,to_gene)

        middle:NodeGene = None

        if replace_index == 0:
            middle:NodeGene = self.getNodeCommon()
            middle.x = (from_gene.x + to_gene.x)/2
            middle.y = (from_gene.y + to_gene.y)/2 + (random.random() * 0.1 - 0.05)
            self.setReplaceIndex(from_gene,to_gene,middle.innovation_number)
        else:
            middle = self.getNode(replace_index)

        

        con1:ConnectionGene = self.getConnection(from_gene,middle)
        con2:ConnectionGene = self.getConnection(middle,to_gene)

        con1.weight = 1
        con2.weight = con.weight
        con2.enabled = con.enabled

        genome.connections.remove(con)
        genome.connections.add(con1)
        genome.connections.add(con2)

        genome.nodes.add(middle)

    def removeExtinctSpecies(self)->None:
        i:int = self.species.size()-1
        while i >= 0:

            # if only representative is left...
            if self.species.get(i).size() <= 1:
                self.species.get(i).goExtinct()
                self.species.removeByIndex(i)

            i -= 1

    def genSpecies(self)->None:
        # reset all except representative
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.reset()

        # iterate and add client to corresponding specie
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            
            if genome.id_specie != -1:
                continue

            found:bool = False
            for j in range(len(self.species.data)):
                s:Specie = self.species.data[j]
                if s.put(genome):
                    found = True
                    break
            
            if not found:
                # create a new specie and the representative will be this new client
                self.species.add(Specie(genome))

        # evaluate scores for each specie
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.evaluateScore()
    
    def kill(self)->None:
        # kill X% of population
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.kill(1-self.SURVIVORS)



