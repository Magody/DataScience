import math
from .Gene import Gene


class Neuron(Gene):

    # type_neuron/x: 0.1->input node, 0.9->output node, other->hidden node
    # if we want to plot the position of this neuron this will be in (x,y)
    x:float = 0
    # y: just a helper to determine its position in network
    y:float = 0

    activation_function = None # type function

    output:float = 0
    connections:list = []  # type: Connection

    def __init__(self,x:float,y:float,innovation_number:int,activation_function=None):
        super().__init__(innovation_number)
        self.x = x
        self.y = y
        self.output:float = 0
        self.connections:list = []  # type: Connection

        if activation_function is None:
            self.activation_function = self.activationFunction
        else:
            self.activation_function = activation_function

    def forward(self):
        s:float = 0
        for i in range(len(self.connections)):
            c:Connection = self.connections[i]
            if c.enabled:
                s += c.weight * c.from_neuron.output

        self.output = self.activationFunction(s)

    def activationFunction(self, x:float)->float:
        # default activation is sigmoid
        return float(1) / (1 + math.exp(-x))

    def equals(self, object):
        if not type(object) is Gene:
            return False
        
        return self.innovation_number == object.innovation_number

    def __str__(self):
        return f"(NodeGene: {self.innovation_number})"

    def hashCode(self):
        return self.innovation_number

class Connection(Gene):
    # crossed reference with Node
    from_neuron:Neuron = None
    to_neuron:Neuron = None
    weight:float = 0
    enabled:bool = True

    replace_index:int = 0

    def __init__(self,from_neuron:Neuron,to_neuron:Neuron):
        self.from_neuron = from_neuron
        self.to_neuron = to_neuron
        self.weight:float = 0
        self.enabled:bool = True
        self.replace_index:int = 0


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
    def getConnectionStatic(con):
        """
        ARG ConnectionGene
        Return ConnectionGene
        """
        c:Connection = Connection(con.from_neuron,con.to_neuron)
        c.innovation_number = con.innovation_number
        c.weight = con.weight
        c.enabled = con.enabled
        return c