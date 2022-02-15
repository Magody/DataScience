from .Gene import Gene

class EnumConnectionTypes:
    TYPE_UNKNOWN = -1
    TYPE_INPUT = 0
    TYPE_HIDDEN = 1
    TYPE_OUTPUT = 2

class Neuron(Gene):
    # GLOBAL/STATIC VARIABLES
    map_neuron_innovation_number:dict = dict() # type <innovation_number:int, sample_x_y:int[2]>. Example: m[2] = (0.1,0.212121)
    

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
        neuron_copy = Neuron(neuron.x,neuron.y,neuron.innovation_number,neuron.activationFunction)
        neuron_copy.output = neuron.output
        return neuron_copy
        
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
        return f"({self.innovation_number})"

    def hashCode(self):
        return self.innovation_number

    @staticmethod
    def getNeuronNew(x:float,y:float,innovation_number:int,activation_function,exist:bool=False):
        n:Neuron = Neuron(x,y,innovation_number,activation_function)
        if not exist:
            # no exist, so add it to storage
            Neuron.map_neuron_innovation_number[innovation_number] = (n.x,n.y,n.activationFunction)
        return n

    @staticmethod
    def getNeuron(innovation_number_expected:int):
        # singleton for x and y for unique innovation_number        

        len_neurons_created:int = len(Neuron.map_neuron_innovation_number)

        exist:bool = False

        innovation_number:int = len_neurons_created + 1
        if innovation_number_expected <= len_neurons_created:
            # in the history this gene was already created
            innovation_number = innovation_number_expected
            sample = Neuron.map_neuron_innovation_number[innovation_number]
            x = sample[0]
            y = sample[1]
            activation_function = sample[2]
            exist = True

            return Neuron.getNeuronNew(x,y,innovation_number,activation_function,True)

        else:
            raise Exception("Unknown neuron: Use getNeuronNew instead")

        
