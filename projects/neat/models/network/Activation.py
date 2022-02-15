import math

class ActivationFunction:

    @staticmethod
    def sigmoid(x:float):
        # default activation is sigmoid
        return 1 / (1 + math.exp(-x))

    
    @staticmethod
    def sigmoid_bounded(x:float):
        # steepened sigmoid: allows more fine tuning at extreme activations. 
        # It's optimized to be close to linear during its steepest ascent between activations
        return 1 / (1 + math.exp(-4.9*x))
