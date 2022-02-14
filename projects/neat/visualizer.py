from multiprocessing import connection
import pygame
from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm



class Button:
    """Create a button, then blit the surface in the while loop"""
 
    def __init__(self, text,  pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", font)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)
 
    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self):
        screen.blit(self.surface, (self.x, self.y))
 
    def click(self, event, callback):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    callback()


WHITE =     (255, 255, 255)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)
TEXTCOLOR = WHITE

CONNECTION_ENABLED = (108, 235, 226)
CONNECTION_DISABLED = (156, 87, 19)

BACKGROUND_COLOR = (  0,   0,  0)




(width, height) = (900, 600)

running = True

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("NEAT")
screen.fill(BACKGROUND_COLOR)
button1 = Button(
    "[0,0]",
    (100, 100),
    font=30,
    bg="navy",
    feedback="You clicked me")
button2 = Button(
    "[0,1]",
    (200, 100),
    font=30,
    bg="navy",
    feedback="You clicked me")
button3 = Button(
    "[1,0]",
    (300, 100),
    font=30,
    bg="navy",
    feedback="You clicked me")
button4 = Button(
    "[1,1]",
    (400, 100),
    font=30,
    bg="navy",
    feedback="You clicked me")

pygame.display.update()

font = pygame.font.Font(None, 24)
font_neuron_output =  pygame.font.Font(None, 20)




######
epochs = 60
global input_size, output_size
input_size = 2 + 1 # + 1 bias

max_population = 1000
output_size = 1

neat:Neat = Neat(input_size,output_size,max_population)

neat.WEIGHT_SHIFT_STRENGTH = 0.5
neat.WEIGHT_RANDOM_STRENGTH = 0.2 # for normal initialization

neat.PROBABILITY_MUTATE_LINK = 0.15
neat.PROBABILITY_MUTATE_NODE = 0.1
neat.PROBABILITY_MUTATE_WEIGHT_SHIFT = 0.1
neat.PROBABILITY_MUTATE_WEIGHT_RANDOM = 0.01
neat.PROBABILITY_MUTATE_TOGGLE_LINK = 0.01

def score(genome:Genome)->float:
    # fitness function: XOR
    global input_size, output_size

    fitness:float = 0

    for i in range(2):
        for j in range(2):

            inp:list = [1,i,j]

            output:list = genome.forward(inp)

            if inp[1] == inp[2]:
                # 0 XOR 0 = 0, 1 XOR 1 = 0
                fitness += (1 - output[0])
            else:
                # 1 XOR 0 = 1, 0 XOR 1 = 1
                fitness += (output[0] - 0)

    return fitness/4


print("EVOLVING PHASE")
for i in tqdm(range(epochs)):
    for j in range(len(neat.genomes.data)):
        genome:Genome = neat.genomes.data[j]
        genome.score = score(genome)
    
    neat.evolve()
    if (i+1)%30 == 0:
        neat.printSpecies()

best_genome = neat.getBestGenomeInSpecies()
    
print(f"BEST SCORE {best_genome.score}")
print(round(best_genome.forward([1,0,0])[0],2))
print(round(best_genome.forward([1,0,1])[0],2))
print(round(best_genome.forward([1,1,0])[0],2))
print(round(best_genome.forward([1,1,1])[0],2))

genome = best_genome
print("HIDDEN CHECK I", genome.hidden_neurons)

connections_expected = best_genome.getConnectionsFromHiddenAndOutput()
print("HIDDEN CHECK II", len(connections_expected))
print("HIDDEN CHECK III", len(best_genome.connections))



#####

def clean():
    screen.fill(BACKGROUND_COLOR)
    pygame.display.update()

def getXYPixel(neuron):
    x = width * neuron.x
    y = height * neuron.y
    return (x,y)


def drawNeuron(neuron,offset=(0,0),color=BLUE):
    (x,y) = getXYPixel(neuron)
    x += offset[0]
    y += offset[1]
    pygame.draw.circle(screen, color, (x,y), 10)
    x -= 5
    y -= 3
    screen.blit(font_neuron_output.render(f"{round(neuron.output,2)}", True, WHITE), (x,y))




def drawConnections(connections:list):

    for i in range(len(connections)):
        connection:Connection = connections[i]

        point_start = getXYPixel(connection.from_neuron)
        point_end = getXYPixel(connection.to_neuron)

        pygame.draw.line(
            screen,
            CONNECTION_ENABLED if connection.enabled else CONNECTION_DISABLED, 
            point_start, 
            point_end
        )

        point_middle = (
            (point_end[0]+point_start[0])/2 - 30,
            (point_end[1]+point_start[1])/2,
        )
        screen.blit(font.render(f"{round(connection.weight,3)}", True, WHITE), point_middle)


def drawGenome(genome:Genome):
    clean()

    

    for neuron in genome.input_neurons:
        drawNeuron(neuron,color=BLUE)

    for neuron in genome.hidden_neurons:
        drawNeuron(neuron,color=(40, 206, 247))

    for i,neuron in enumerate(genome.output_neurons):
        drawNeuron(neuron,color=(125, 25, 60))

    drawConnections(genome.connections)

   
    

    pygame.display.update()

######


def callbackForward1():
    genome.forward([1,0,0])
    drawGenome(genome)

def callbackForward2():
    genome.forward([1,0,1])
    drawGenome(genome)

def callbackForward3():
    genome.forward([1,1,0])
    drawGenome(genome)

def callbackForward4():
    genome.forward([1,1,1])
    drawGenome(genome)

drawGenome(genome)

while running:
    ev = pygame.event.get()

    button1.show()
    button2.show()
    button3.show()
    button4.show()
    pygame.display.update()

    for event in ev:
        button1.click(event, callbackForward1)
        button2.click(event, callbackForward2)
        button3.click(event, callbackForward3)
        button4.click(event, callbackForward4)
        

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                genome = neat.empty_genome()
                clean()
                drawGenome(genome)

            if event.key == pygame.K_t:
                drawGenome(genome)

            if event.key == pygame.K_a:
                neat.mutateGenomeNode(genome)
                drawGenome(genome)
            
            if event.key == pygame.K_s:
                neat.mutateGenomeLink(genome)
                drawGenome(genome)

            if event.key == pygame.K_d:
                genome.mutateLinkToggle()
                drawGenome(genome)
            
            if event.key == pygame.K_w:
                genome.mutateWeightRandom(neat.WEIGHT_RANDOM_STRENGTH)
                drawGenome(genome)
            
            if event.key == pygame.K_e:
                genome.mutateWeightShift(neat.WEIGHT_SHIFT_STRENGTH)
                drawGenome(genome)


        if event.type == pygame.QUIT:
            running = False
