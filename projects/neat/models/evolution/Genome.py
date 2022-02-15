import random

from ..data_structures.RandomHashSet import RandomHashSet
from ..network.Neuron import *
from ..network.Network import *




class Genome(Network):

    score:float = 0

    id_specie: int = -1

    mutation_rates = dict()


    def __init__(
        self,
        input_neurons:list,
        hidden_neurons:list,
        output_neurons:list,
        probability_mutate_connections_weight:float = 0.8,
        probability_perturb:float = 0.9,
        probability_mutate_link:float = 0.06, # larger population may need 0.3+ because a larger population can tolerate a larger number of prospective species and greater topological diversity.
        probability_mutate_node:float = 0.05,
        probability_mutate_enable:float = 0.2,
        probability_mutate_disable:float = 0.1,
        # depending on these, everything will work or not
        weight_step:float = 0.01, 
        MAX_HIDDEN_NEURONS:int = 10      
    ):
        super().__init__(input_neurons,hidden_neurons,output_neurons)
        self.MAX_HIDDEN_NEURONS:int = MAX_HIDDEN_NEURONS

        self.id_specie = -1
        self.score:float = 0

        # Mutation properties
        self.mutation_rates = dict()


        self.mutation_rates["connection_weight"] = probability_mutate_connections_weight
        self.mutation_rates["link"] = probability_mutate_link
        self.mutation_rates["node"] = probability_mutate_node
        self.mutation_rates["enable"] = probability_mutate_enable
        self.mutation_rates["disable"] = probability_mutate_disable
        self.mutation_rates["step"] = weight_step

        self.probability_perturb = probability_perturb

    @staticmethod
    def copy(genome, copy_specie=True):

        # todo: check copy method is correct
        genome_copy:Genome = Genome(
            [],
            [],
            [],
            probability_mutate_connections_weight=genome.mutation_rates["connection_weight"],
            probability_perturb=genome.probability_perturb,
            probability_mutate_link=genome.mutation_rates["link"],
            probability_mutate_node=genome.mutation_rates["node"],
            probability_mutate_enable=genome.mutation_rates["enable"],
            probability_mutate_disable=genome.mutation_rates["disable"],
            weight_step=genome.mutation_rates["step"],
            MAX_HIDDEN_NEURONS=genome.MAX_HIDDEN_NEURONS
        )


        if copy_specie:
            genome_copy.id_specie = genome.id_specie
        genome_copy.score = genome.score
        genome_copy.probability_perturb = genome.probability_perturb

        

        for innovation_number,neuron in genome.neurons.items():
            genome_copy.insertNeuron(Neuron.copy(neuron))

        for connection in genome.connections:
            
            neuronFrom, neuronTo = genome_copy.getSingletonContainers(connection)
            genome_copy.insertConnection(Connection.copy(connection,neuronFrom, neuronTo))

        return genome_copy


    def evaluateInput(self,input:list)->list:
        return self.forward(input)

    def mutateConnectionWeights(self):
        # The system is tolerant to frequent mutations (source:paper)
        # todo: check if changes is for all connections or random
        # for connection in self.connections:

        connection:Connection = self.getRandomConnection()

        if connection:
            # just change one at a time
            if random.random() < self.probability_perturb:
                connection.weight = connection.weight + Connection.getRandomWeight(multiplier_range=1) * self.mutation_rates["step"] # todo:check value
            else:
                connection.weight = Connection.getRandomWeight(multiplier_range=0.5)


    def mutateRandomLinkToggle(self, toggle_to_enabled):
        # todo: optimice
        connections_valid:list = []

        for connection in self.connections:
            if toggle_to_enabled:
                if not connection.enabled:
                    connections_valid.append(connection)
            else:
                if connection.enabled:
                    connections_valid.append(connection)

        len_connections_valid = len(connections_valid)
        if len_connections_valid == 0:
            return
        
        connections_valid[random.randint(0,len_connections_valid-1)].enabled = toggle_to_enabled

    
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
    def crossover(g1, g2, genome, probability_preserve_disabled=0.75):
        """ 
        g1 has to be the genome with highest score.
        """
        # todo: # check that crossover is well done, pass by reference works and genome new modify only needed

        # genome is a "empty" base genome with existing or no nodes

        index_g1 = 0
        index_g2 = 0

        # Connections have to be sorted for this alignment
        while index_g1 < len(g1.connections) and index_g2 < len(g2.connections):

            connection1:Connection = g1.connections[index_g1]
            connection2:Connection = g2.connections[index_g2]

            in1:int = connection1.innovation_number
            in2:int = connection2.innovation_number

            if in1 == in2:
                connection_inherit:Connection = None
                # similar gene
                if random.random() < 0.5:
                    # create or retrieve containers if exist
                    neuronFrom, neuronTo = genome.getSingletonContainers(connection1)
                    connection_inherit = Connection.copy(connection1,neuronFrom, neuronTo)
                else:
                    neuronFrom, neuronTo = genome.getSingletonContainers(connection2)
                    connection_inherit = Connection.copy(connection2,neuronFrom, neuronTo)

                if not connection1.enabled or not connection2.enabled:
                    #paper: "There was a n% chance that an inherited gene was disabled if it was disabled in either parent."
                    if connection_inherit.enabled and random.random() < probability_preserve_disabled:
                        connection_inherit.enabled = False

                genome.insertConnection(connection_inherit)

                index_g1 += 1
                index_g2 += 1
            elif in1 > in2:
                # disjoint gene of b
                # g1 has better score, so g2 is discarded
                index_g2 += 1
            else:
                # disjoint gene of a
                # g1 has better score, so preserve the gene
                neuronFrom, neuronTo = genome.getSingletonContainers(connection1)
                connection_inherit = Connection.copy(connection1,neuronFrom, neuronTo)
                genome.insertConnection(connection_inherit)
                index_g1 += 1

        # before = [index_g1,len(genome.connections)]

        # if before[1] == 0 and len(g1.connections) == 2:
        #   print()

        while index_g1 < len(g1.connections):
            # todo: check if this is useful
            connection1:Connection = g1.connections[index_g1]
            # create or retrieve neurons
            neuronFrom, neuronTo = genome.getSingletonContainers(connection1)
            connection_inherit = Connection.copy(connection1,neuronFrom, neuronTo)

            genome.insertConnection(connection_inherit)
            index_g1 += 1
            
        
        # the mutation rates may have been modified 
        for mutation,rate in g1.mutation_rates.items():
            genome.mutation_rates[mutation] = rate

        """
        if len(g1.connections) != len(g2.connections):
            print(g1)
            print("+")
            print(g2)
            print("==========")
            print(genome)
            print()
        """

        return genome

    def __str__(self)->str:

        output:str = ""
        for connection in self.connections:
            output += f"{connection.innovation_number}-{round(connection.weight,2)}-{connection.enabled}: {connection.neuronFrom.innovation_number}->{connection.neuronTo.innovation_number} | "

        return output
        