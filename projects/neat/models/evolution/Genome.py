import random

from ..network.Neuron import *
from ..network.Connection import *
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
        probability_mutate_connections_weight:float = 0.8, # ->0.8
        probability_perturb:float = 0.9, # ->0.9
        probability_mutate_link:float = 0.2, # ->0.06 larger population may need 0.3+ because a larger population can tolerate a larger number of prospective species and greater topological diversity.
        probability_mutate_node:float = 0.1, # ->0.05
        probability_mutate_enable:float = 0.1, # ->0.2
        probability_mutate_disable:float = 0.05, # ->0.1
        # depending on these, everything will work or not
        std_weight_initialization:float = 1,
        weight_step:float = 0.01, # ->0.01
        MAX_HIDDEN_NEURONS:int = 3
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
        self.mutation_rates["std_weight_initialization"] = std_weight_initialization

        self.probability_perturb = probability_perturb

    @staticmethod
    def empty_genome(input_size:int, output_size:int, prefill:bool=True, connect_input_output:bool=True):

        input_neurons:list = []
        output_neurons:list = []

        if prefill:

            for innovation_number in range(1, input_size+1):
                input_neurons.append(Neuron.getNeuron(innovation_number))

            for innovation_number in range(input_size+1,input_size+output_size+1):
                output_neurons.append(Neuron.getNeuron(innovation_number))

        genome = Genome(input_neurons,[],output_neurons)
        if connect_input_output:
            # initial connection
            for input_neuron in genome.input_neurons:
                for output_neuron in genome.output_neurons:
                    genome.insertConnection(Connection.getConnection(input_neuron,output_neuron))

        return genome

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

    def mutate(self)->None:
        # alter the rate for every mutation 
        for mutation,rate in self.mutation_rates.items():
            if random.random() < 0.5:
                self.mutation_rates[mutation] = 0.99 * rate
            else:
                self.mutation_rates[mutation] = 1.01 * rate
            

        # mutate weights
        p1:float = random.random()
        if p1 < self.mutation_rates["connection_weight"]:
            # if mutate, exist a probability of become weights random or just do a step
            self.mutateConnectionWeights()

        # mutate link
        p2:float = random.random()
        if p2 < self.mutation_rates["link"]:
            self.mutateGenomeLink()

        # increment nodes if possible
        if len(self.hidden_neurons) < self.MAX_HIDDEN_NEURONS:
            p3:float = random.random()
            if p3 < self.mutation_rates["node"]:
                self.mutateGenomeNode()

        p4:float = random.random()
        if p4 < self.mutation_rates["enable"]:
            self.mutateRandomLinkToggle(toggle_to_enabled=True)

        p5:float = random.random()
        if p5 < self.mutation_rates["disable"]:
            self.mutateRandomLinkToggle(toggle_to_enabled=False)


    def mutateGenomeLink(self)->bool:
        # todo: improve search selection. important!
        added:bool = False
        for _ in range(100):
            a, b = self.getRandomGenePair()

            con:Connection = None
            if a.x < b.x:
                con = Connection(a,b)
            else:
                con = Connection(b,a)


            con = Connection.getConnection(con.neuronFrom, con.neuronTo)

            if self.existConnection(con.innovation_number):
                # if exists or is not set to False, return
                continue

            con.weight = Connection.getRandomWeight(multiplier_range=0.5)

            
            self.insertConnection(con)
            added = True
            break
        return added

    def mutateGenomeNode(self):
        # add hidden node in EXISTING connection
        con:Connection = self.getRandomConnection()
        
        if con is None:
            # there is no connections yet
            return
        

        from_neuron:Neuron = con.neuronFrom
        to_neuron:Neuron = con.neuronTo

        # always split the link into two nodes
        replace_index, key = Connection.getReplaceIndex(from_neuron,to_neuron)

        middle:Neuron = None

        create_new_node:bool = True

        if replace_index > 0:
            # already exist a node in the connection
            if not self.existNeuronInnovationNumber(replace_index):
                # If already exist a neuron in general, but not in genome, create a copy
                middle = Neuron.getNeuron(replace_index)
                create_new_node = False
        
        if create_new_node:
            # if no previous neuron was created between this connection
            x = (from_neuron.x + to_neuron.x)/2
            y = (from_neuron.y + to_neuron.y)/2 + (random.random() * 0.1 - 0.05)
            innovation_number:int = len(Neuron.map_neuron_innovation_number)+1
            middle:Neuron = Neuron.getNeuronNew(x,y,innovation_number,self.activationFunctionHidden)
            Connection.setReplaceIndex(from_neuron,to_neuron,middle.innovation_number)
        

        con1:Connection = Connection.getConnection(from_neuron,middle)
        con2:Connection = Connection.getConnection(middle,to_neuron)

        # before link: set weight to 1
        con1.weight = 1
        # next link: restore the properties of original long connection
        con2.weight = con.weight
        con2.enabled = con.enabled

        # if input [1,2,3] and output [4]
        # adding hidden node is hidden [5]
        # originally 1->4, and we want to put the node 5 in middle
        # now 1->5->4. the original connection 1->4 have to be removed
        # genome.removeConnection(con) If we remove, then in a mutation will create it again... a loop forever
        con.enabled = False
        # the middle is a brand new or existing in general storage mapping
        self.insertNeuron(middle)

        # now we add the segmented connection
        self.insertConnection(con1)
        self.insertConnection(con2)


    def mutateConnectionWeights(self):
        # The system is tolerant to frequent mutations (source:paper)
        # todo: check if changes is for all connections or random
        for connection in self.connections:

            # connection:Connection = self.getRandomConnection()

            if connection:
                # just change one at a time
                if random.random() < self.probability_perturb:
                    random_weight:float = Connection.getRandomWeight(multiplier_range=1)
                    connection.weight = connection.weight + (random_weight * self.mutation_rates["step"]) # todo:check value
                else:
                    connection.weight = Connection.getRandomWeight(multiplier_range=self.mutation_rates["std_weight_initialization"])

                """
                CLAMP WEIGHTS:
                if connection.weight > 1:
                    connection.weight = 1
                elif connection.weight < -1:
                    connection.weight = -1
                """


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
        