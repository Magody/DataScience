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

font = pygame.font.Font(None, 16)
font_neuron_output =  pygame.font.Font(None, 30)




######
neat = None
global current_input
current_input = [1,0,0]
def run_experiment(seed,verbose_level=0):

    # replicate experiment
    random.seed(seed)

    epochs = 200 # 100 in paper
    global input_size, output_size
    input_size = 2 + 1 # + 1 bias

    max_population = 300 # 150 in paper
    output_size = 1

    neat:Neat = Neat(
        input_size,output_size,max_population
    )

    global current_input
    current_input = [1,0,0]

    

    def scoreAND(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == 1 and inp[2] == 1:
                    # 1
                    fitness += output[0]
                else:
                    # 0
                    fitness += (1 - output[0])

        # maximum can get: 4
        return fitness * fitness # square for sparse more the fitness and do better selections


    def scoreOR(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == 1 or inp[2] == 1:
                    # 1
                    fitness += output[0]
                else:
                    # 0
                    fitness += (1 - output[0])

        # maximum can get: 4
        final_fitness = fitness * fitness
        final_fitness_with_penalization = final_fitness
        return final_fitness_with_penalization # square for sparse more the fitness and do better selections


    def scoreXOR(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == inp[2]:
                    # Expected: 0
                    fitness += (1 - output[0])
                else:
                    # Expected: 1
                    fitness += output[0]


        # maximum can get: 4
        return fitness * fitness # square for sparse more the fitness and do better selections


    print("EVOLVING PHASE")
    debug_step = epochs//10 # epochs//10 
    for i in tqdm(range(epochs)):
        # we can collect scores by frame, in this case we can directly collect from functions
        for j in range(len(neat.genomes)):
            genome:Genome = neat.genomes[j]
            genome.score = scoreXOR(genome)
        
        neat.evolve(verbose_level=verbose_level-1,debug_step=debug_step)
            

    best_genome = neat.getBestGenome()

    operator = "&"
    
    
    if verbose_level > 0:
        print(f"BEST SCORE {best_genome.score}")
        print("CONNECTIONS: ", len(best_genome.connections))
        print(f"0 {operator} 0 =", round(best_genome.forward([1,0,0])[0],2))
        print(f"0 {operator} 1 =", round(best_genome.forward([1,0,1])[0],2))
        print(f"1 {operator} 0 =", round(best_genome.forward([1,1,0])[0],2))
        print(f"1 {operator} 1 =", round(best_genome.forward([1,1,1])[0],2))

    global genome_draw
    genome_draw = best_genome

    #for specie in neat.species.data:
    #    print(f"Specie {specie.id} sample: {specie.representative}")
    return best_genome.score

run_experiment(1,1)


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
    pygame.draw.circle(screen, color, (x,y), 12)
    x -= 5
    y -= 3
    screen.blit(font_neuron_output.render(f"{round(neuron.output,2)}", True, WHITE), (x,y))




def drawConnections(connections:list):

    for i in range(len(connections)):
        connection:Connection = connections[i]

        point_start = getXYPixel(connection.neuronFrom)
        point_end = getXYPixel(connection.neuronTo)

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

    global current_input
    genome.forward(current_input)

    

    for neuron in genome.input_neurons:
        drawNeuron(neuron,color=BLUE)

    for neuron in genome.hidden_neurons:
        drawNeuron(neuron,color=(59, 94, 68))

    for i,neuron in enumerate(genome.output_neurons):
        drawNeuron(neuron,color=(125, 25, 60))

    drawConnections(genome.connections)

   
    

    pygame.display.update()

######


def callbackForward1():
    global current_input, genome_draw
    current_input = [1,0,0]
    drawGenome(genome_draw)

def callbackForward2():
    global current_input, genome_draw
    current_input = [1,0,1]
    drawGenome(genome_draw)

def callbackForward3():
    global current_input, genome_draw
    current_input = [1,1,0]
    drawGenome(genome_draw)

def callbackForward4():
    global current_input, genome_draw
    current_input = [1,1,1]
    drawGenome(genome_draw)

#genome_draw = neat.empty_genome()

global genome_draw
drawGenome(genome_draw)

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
                genome_draw = neat.empty_genome()
                clean()
                drawGenome(genome_draw)

            if event.key == pygame.K_t:
                drawGenome(genome_draw)

            if event.key == pygame.K_a:
                neat.mutateGenomeNode(genome_draw)
                drawGenome(genome_draw)
            
            if event.key == pygame.K_s:
                neat.mutateGenomeLink(genome_draw)
                drawGenome(genome_draw)

            if event.key == pygame.K_d:
                genome_draw.mutateRandomLinkToggle()
                drawGenome(genome_draw)
            
            if event.key == pygame.K_w:
                genome_draw.mutateConnectionWeights()
                drawGenome(genome_draw)


        if event.type == pygame.QUIT:
            running = False
