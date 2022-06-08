
import timeit
import random
import time
from deap import base, creator, tools, algorithms
from py4j.java_gateway import JavaGateway, CallbackServerParameters

from OptimizationModel.evaluation import Evaluation


class Optimization:

    NOBJ = 0
    def __init__(self, pop_size, num_generations, solution_technique, weighted_sum, VmSize,gpuVmSize, hostSize,gpuhostSize, hostCnt,gpuhostCnt, VmCnt,gpuVmCnt):

        gateway = JavaGateway(callback_server_parameters=CallbackServerParameters())
        
        self.gateway = gateway
        self.weighted_sum = weighted_sum
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.cxpb = 0.3
        self.mutpb = 0.1
        self.solution_technique = solution_technique
        self.toolbox = base.Toolbox()
        self.pareto_dict = {}
        self.objective_dict = {}

        self.hostSize = hostSize
        self.gpuhostSize = gpuhostSize
        self.VmCnt = VmCnt
        self.gpuVmCnt = gpuVmCnt
        self.hostCnt = hostCnt
        self.gpuhostCnt = gpuhostCnt
        self.VmSize = VmSize
        self.gpuVmSize = gpuVmSize


        if len(self.weighted_sum) != 0:
            self.pareto_front = tools.HallOfFame(30)
        else:
            self.pareto_front = tools.ParetoFront()
        # instantiate Evaluation Class
        self.evaluation_instance = Evaluation(self.gateway)

        # instead of evalFitness pass an interface to the Simulation in JAVA
        # register on the interface that you will create a method that will invoke the java code base

        self.toolbox.register("evaluate", self.evaluation_instance.evalBridge)

        if solution_technique == 'Metaheuristic_GA':
            self.genetic_algorithms()

        elif solution_technique == 'Metaheuristic_NSGA3':
            self.NSGA3()

        else:
            print('\n## Initialization error ## \n-Two solution techniques are available: Metaheuristic_NSGA3, and Metaheuristic_GA \n-Note: The naming is case-sensitive')

        self.run_metaheuristic_optimization()

    def genetic_algorithms(self):

        random.seed(time.process_time())

        # register toolboxes functions for the genetic algorithm
        #
        self.toolbox.register("VmAllocation",VmAllocation,self.VmCnt)
        self.toolbox.register("GpuVmAllocation", GpuVmAllocation, self.gpuVmCnt)
        self.toolbox.register("HostAllocation",HostAllocation,self.hostCnt)
        self.toolbox.register("GpuHostAllocation", GpuHostAllocation, self.gpuhostCnt)
        #function container with a generator function corresponding to the calling n times the functions
        self.toolbox.register("individual", tools.initCycle, creator.Individual_allocation, (self.toolbox.VmAllocation,
                                                                                             self.toolbox.HostAllocation,
                                                                                             self.toolbox.GpuVmAllocation,
                                                                                             self.toolbox.GpuHostAllocation,
                                                                                             ),n=1)
        #Call the function func n times and return the results in a container type container
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        #Executes a uniform crossover that modify in place the two sequence individuals.
        #The attributes are swapped according to the indpb probability.
        self.toolbox.register("mate", tools.cxUniform, indpb=0.7)
        #self.toolbox.register("mate", tools.cxTwoPoint )

        #Shuffle the attributes of the input individual and return the mutant
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
        #self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=10)
        #self.toolbox.register("select", tools.selBest,individuals=4, k=2, fit_attr="fitness")

    def run_metaheuristic_optimization(self):

        self.start = timeit.default_timer()
        population = self.toolbox.population(n=self.pop_size)

        for gen in range(self.num_generations):

            print('------------- Processing Generation:', gen, '-------------')
            if gen == 0:
                offspring = population
            else:
                offspring = algorithms.varAnd(population, self.toolbox, cxpb=self.cxpb, mutpb=self.mutpb)

            fits = self.toolbox.map(self.toolbox.evaluate, offspring)

            #offspring is a list of individuals and fits is a list of fitnesses ()

            for fit, ind in zip(fits, offspring):
                individual_index = offspring.index(ind)
                key = individual_index + (gen * self.pop_size)
                #ExecTime: when the last cloudlet finish execution
                self.ExecTime = fit[0]
                self.TotalPower = fit[1]
                self.TotalCost = fit[2]

                self.normalized_fitness = self.normalize_results_minMax(fit)

                if len(self.weighted_sum) != 0:
                    self.tensor_fitness = self.normalized_fitness
                    self.objective_dict[key] = [self.ExecTime, self.TotalPower, self.TotalCost,
                                                self.tensor_fitness]
                    ind.fitness.values = self.normalized_fitness,
                else:
                    self.tensor_fitness = sum(self.normalized_fitness) * 10
                    self.objective_dict[key] = [self.ExecTime, self.TotalPower, self.TotalCost,
                                                self.tensor_fitness]
                    ind.fitness.values = self.normalized_fitness


            self.pareto_front.update(population)

            if self.solution_technique == 'Metaheuristic_GA':
                population = self.toolbox.select(offspring, self.pop_size)
            else:
                population = self.toolbox.select(population + offspring, self.pop_size)


        print('\n##### Computational time of the optimization:', (timeit.default_timer() - self.start) / 60,'minutes #####')
        print('-------------------------------------------------------------------------------')

    def normalize_results_minMax(self, fitness):

        ### Normalization ########################################################################

        ExecTime = fitness[0]  # ExecTime
        ExecTimeMin = 30
        ExecTimeMax = 120

        if ExecTimeMax - ExecTimeMin == 0:
            normalizedExecTime = 1
        else:
            normalizedExecTime = (ExecTime - ExecTimeMin) / (ExecTimeMax - ExecTimeMin)

        Power = fitness[1]  # Total Power
        PowerMin = 0
        PowerMax = 1000

        if PowerMax - PowerMin == 0:
            normalizedPower = 1
        else:
            normalizedPower = (Power - PowerMin) / (PowerMax - PowerMin)


        ### Fittness #############################################################################

        if len(self.weighted_sum) != 0:

            fitness = self.weighted_sum[0] * normalizedExecTime + \
                      self.weighted_sum[1] * normalizedPower
        else:
            fitness = (normalizedPower, normalizedExecTime)

        return fitness

#Number of vm adaptation
def VmAllocation(self):
    vmNumber = self
    vmTuple = []
    for i in (1,2,3):
        if i == 1 :
            RandvmCnt = random.randrange(vmNumber)
            newvmNumber = vmNumber - RandvmCnt
            vmTuple.append([i,RandvmCnt])
        elif i == 2:
            newRandvmCnt = random.randrange(newvmNumber)
            vmTuple.append([i,newRandvmCnt])
        elif i == 3 :
            treenewvmNumber = vmNumber - (RandvmCnt+newRandvmCnt)
            vmTuple.append([i, treenewvmNumber])
        else: print(   "invalid vm Size"   )
    print("vm Tuple: ",vmTuple)
    return vmTuple

def GpuVmAllocation(self):
    vmNumber = self
    gpuvmTuple = []
    for i in (1,2,3):
        if i == 1 :
            RandvmCnt = random.randrange(vmNumber)
            newvmNumber = vmNumber - RandvmCnt
            gpuvmTuple.append([i,RandvmCnt])
        elif i == 2:
            newRandvmCnt = random.randrange(newvmNumber)
            gpuvmTuple.append([i,newRandvmCnt])
        elif i == 3 :
            treenewvmNumber = vmNumber - (RandvmCnt+newRandvmCnt)
            gpuvmTuple.append([i, treenewvmNumber])
        else: print(   "invalid vm Size"   )
    print("Gpuvm Tuple: ",gpuvmTuple)
    return gpuvmTuple


#Number of hosts adaptation
def HostAllocation(self):
    vmNumber = self
    hostTuple = []
    for i in (1, 2, 3):
        RandHost = random.randrange(int(vmNumber/3), vmNumber)
        hostTuple.append([i,RandHost])
    print("host Tuple: ",hostTuple)
    return hostTuple

def GpuHostAllocation(self):
    gpuvmNumber = self
    gpuhostTuple = []
    for i in (1, 2, 3):
        RandHost = random.randrange(int(gpuvmNumber/3), gpuvmNumber)
        gpuhostTuple.append([i,RandHost])
    print("Gpuhost Tuple: ",gpuhostTuple)
    return gpuhostTuple