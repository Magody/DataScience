import random

class RandomSelector:

    objects = []  # <T>
    scores = [] # double

    total_score = 0 # double

    def __init__(self):

        self.objects = []
        self.scores = [] # double
        self.total_score = 0 # double

    def add(self,element, score:float):
        self.objects.append(element)
        self.scores.append(score)
        self.total_score += score

    def random(self):
        v: float = random.random() * self.total_score
        c: float = 0
        for i in range(len(self.objects)):
            c += self.scores[i]
            if c >= v:
                return self.objects[i]
        return None

    def reset(self):
        self.objects.clear()
        self.scores.clear()
        self.total_score = 0