import math
import random
from .Gene import Gene

class EnumConnectionTypes:
    TYPE_UNKNOWN = -1
    TYPE_INPUT = 0
    TYPE_HIDDEN = 1
    TYPE_OUTPUT = 2

class Neuron(Gene):

    # type_neuron/x: 0.1->input node, 0.9->output node, other->hidden node
    # if we want to plot the position of this neuron this will be in (x,y)
    x:float = 0
    # y: just a helper to determine its position in network
    y:float = 0

    activationFunction = None # type function

    output:float = 0


    def __init__(self,x:float,y:float,innovation_number:int,activationFunction):
        super().__init__(innovation_number)
        self.x = x
        self.y = y
        self.output:float = 0

        self.activationFunction = activationFunction

    @staticmethod
    def copy(neuron):
        # Neurons have to be passed by reference, are shared by connections
        return neuron
        """
        neuron_copy = Neuron(neuron.x,neuron.y,neuron.innovation_number,neuron.activationFunction)
        neuron_copy.output = neuron.output
        return neuron_copy
        """
    def getNeuronType(self)->int:

        x_destiny:float = self.x
        # assume the connection is from input/hidden to hidden
        connection_type:int = EnumConnectionTypes.TYPE_HIDDEN
        
        if x_destiny == 0.1:
            connection_type = EnumConnectionTypes.TYPE_INPUT
        elif x_destiny == 0.9:
            # the connection comes from input/hidden to output
            connection_type = EnumConnectionTypes.TYPE_OUTPUT

        return connection_type



    def equals(self, object):
        if not type(object) is Gene:
            return False
        
        return self.innovation_number == object.innovation_number

    def __str__(self):
        return f"(Neuron: {self.innovation_number})"

    def hashCode(self):
        return self.innovation_number

class Connection(Gene):
    # This neurons are copyies and share same innovation number with others
    from_neuron:Neuron = None
    to_neuron:Neuron = None
    weight:float = 0
    enabled:bool = True

    replace_index:int = 0

    def __init__(self,from_neuron:Neuron,to_neuron:Neuron):
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight:float = Connection.getRandomWeight(0.5)
        self.enabled:bool = True
        self.replace_index:int = 0

    @staticmethod
    def copy(connection):
        # todo: optimize?
        connection_copy:Connection = Connection(Neuron.copy(connection.from_neuron),Neuron.copy(connection.to_neuron))
        connection_copy.weight = connection.weight
        connection_copy.enabled = connection.enabled
        connection_copy.replace_index = connection.replace_index # todo: check replace index
        connection_copy.innovation_number = connection.innovation_number

        return connection_copy



    def equals(self, object):
        if not type(object) is Connection:
            return False
        
        return self.from_neuron.equals(object.from_neuron) and self.to_neuron.equals(object.to_neuron)

    def __str__(self):
        return f"(Connection: from={self.from_neuron.innovation_number},to={self.to_neuron.innovation_number},weight={self.weight},enabled={self.enabled},innovation_number={self.innovation_number})"

    def hashCode(self)->int:
        MAX_NODES = math.pow(2,20)
        return int(self.from_neuron.innovation_number * MAX_NODES + self.to_neuron.innovation_number)
    
    @staticmethod
    def getConnectionType(connection)->int:
         # interpret the place of connection
        return connection.to_neuron.getNeuronType()

    @staticmethod
    def getRandomWeight(multiplier_range=1):
        return (random.random() * 2 - 1) * multiplier_range
