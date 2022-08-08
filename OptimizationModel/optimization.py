import timeit
import random
import time
from deap import base, creator, tools, algorithms
from py4j.java_gateway import JavaGateway, CallbackServerParameters

from OptimizationModel.evaluation import Evaluation


class Optimization:
    NOBJ = 0

    def __init__(self, pop_size, num_generations, solution_technique, weighted_sum, gateway):

        self.gateway = gateway
        #self.Jobset = Jobset
        self.weighted_sum = weighted_sum
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.cxpb = 0.8
        self.mutpb = 0.5
        self.solution_technique = solution_technique
        self.toolbox = base.Toolbox()
        self.pareto_dict = {}
        self.objective_dict = {}

        #self.initSetup = initSetup

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
            print(
                '\n## Initialization error ## \n-Two solution techniques are available: Metaheuristic_NSGA3, and Metaheuristic_GA \n-Note: The naming is case-sensitive')

        self.run_metaheuristic_optimization()

    def genetic_algorithms(self):

        number_jobs = 199
        random.seed(time.process_time())

        # register toolboxes functions for the genetic algorithm
        # self.toolbox.register("Matrix", SuffleM, self.initSetup)
        # Initialize different rages of attributes, which must be used for create individuals

        self.toolbox.register("vm_size", random.randint, 1, 3)
        self.toolbox.register("exec_sequence", random.randint, 1, 6)
        self.toolbox.register("allocation_policy", random.randint, 1, 3)

        # Define the shape of individuals across different populations
        self.toolbox.register("individual_vm_size", tools.initCycle, creator.Individual_vm_size,
                              (self.toolbox.vm_size,), n=number_jobs)
        self.toolbox.register("individual_exec_sequence", tools.initCycle, creator.Individual_exec_sequence,
                              (self.toolbox.exec_sequence,), n=number_jobs)
        self.toolbox.register("individual_allocation_policy", tools.initCycle, creator.Individual_allocation_policy,
                              (self.toolbox.allocation_policy,), n=number_jobs)

        # Call the function func n times and return the results in a container type container
        self.toolbox.register("vm_size_population", tools.initRepeat, list, self.toolbox.individual_vm_size)
        self.toolbox.register("exec_sequence_population", tools.initRepeat, list, self.toolbox.individual_exec_sequence)
        self.toolbox.register("allocation_policy_population", tools.initRepeat, list, self.toolbox.individual_allocation_policy)

        # Executes a uniform crossover that modify in place the two sequence individuals.
        # The attributes are swapped according to the indpb probability.
        self.toolbox.register("mate", tools.cxUniform, indpb=0.7)
        # self.toolbox.register("mate", tools.cxTwoPoint )

        # Shuffle the attributes of the input individual and return the mutant
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
        # self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=1)
        # self.toolbox.register("select", tools.selBest,individuals=4, k=2, fit_attr="fitness")


    def NSGA(self):

        P = 3
        number_jobs = 10
        random.seed(time.process_time())

        # register toolboxes functions for the genetic algorithm
        # self.toolbox.register("Matrix", SuffleM, self.initSetup)
        # Initialize different rages of attributes, which must be used for create individuals

        self.toolbox.register("vm_size", random.randint, 1, 3)
        self.toolbox.register("exec_sequence", random.randint, 1, 6)
        self.toolbox.register("allocation_policy", random.randint, 1, 3)

        # Define the shape of individuals across different populations
        self.toolbox.register("individual_vm_size", tools.initCycle, creator.Individual_vm_size,
                              (self.toolbox.vm_size,), n=number_jobs)
        self.toolbox.register("individual_exec_sequence", tools.initCycle, creator.Individual_exec_sequence,
                              (self.toolbox.exec_sequence,), n=number_jobs)
        self.toolbox.register("individual_allocation_policy", tools.initCycle, creator.Individual_allocation_policy,
                              (self.toolbox.allocation_policy,), n=number_jobs)

        # Call the function func n times and return the results in a container type container
        self.toolbox.register("vm_size_population", tools.initRepeat, list, self.toolbox.individual_vm_size)
        self.toolbox.register("exec_sequence_population", tools.initRepeat, list, self.toolbox.individual_exec_sequence)
        self.toolbox.register("allocation_policy_population", tools.initRepeat, list, self.toolbox.individual_allocation_policy)

        # Executes a uniform crossover that modify in place the two sequence individuals.
        # The attributes are swapped according to the indpb probability.
        self.toolbox.register("mate", tools.cxUniform, indpb=0.7)
        # self.toolbox.register("mate", tools.cxTwoPoint )

        # Shuffle the attributes of the input individual and return the mutant
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
        # self.toolbox.register("mutate", tools.mutFlipBit, indpb=0.2)
        self.ref_points = tools.uniform_reference_points(Optimization.NOBJ, P)
        self.toolbox.register("select", tools.selNSGA3, ref_points=self.ref_points)
        # self.toolbox.register("select", tools.selBest,individuals=4, k=2, fit_attr="fitness")

    def run_metaheuristic_optimization(self):

        """
        Shape:
        creator.create("Individual_vm_size", list, fitness=creator.FitnessMin, Individual_exec_sequence=None,
                       Individual_allocation_policy=None)
        creator.create("Individual_exec_sequence", list, fitness=creator.FitnessMin)
        creator.create("Individual_allocation_policy", list, fitness=creator.FitnessMin)
        which replace these random values
        Size = random.randint(1, 3)
        Seq = random.randint(1, 6)
        allocationpolicy = random.randint(1, 3)
        """


        self.start = timeit.default_timer()

        vm_size_population = self.toolbox.vm_size_population(n=self.pop_size)
        exec_sequence_population = self.toolbox.exec_sequence_population(n=self.pop_size)
        allocation_policy_population = self.toolbox.allocation_policy_population(n=self.pop_size)

        for gen in range(self.num_generations):

            print('------------- Processing Generation:', gen, '-------------')

            if gen == 0:
                vm_size_offspring = vm_size_population
                exec_sequence_offspring = exec_sequence_population
                allocation_policy_offspring = allocation_policy_population
            else:
                vm_size_offspring = algorithms.varAnd(vm_size_population, self.toolbox, cxpb=self.cxpb,
                                                      mutpb=self.mutpb)
                exec_sequence_offspring = algorithms.varAnd(exec_sequence_population, self.toolbox, cxpb=self.cxpb,
                                                            mutpb=self.mutpb)
                allocation_policy_offspring = algorithms.varAnd(allocation_policy_population, self.toolbox,
                                                                cxpb=self.cxpb,
                                                                mutpb=self.mutpb)
            """
                Here we are merging the individuals and passing them at attribute to the main population
            """

            for vm_size_individual, exec_sequence_individual, allocation_policy_individual in zip(vm_size_offspring,
                                                                                                  exec_sequence_offspring,
                                                                                                  allocation_policy_offspring):
                vm_size_individual.Individual_exec_sequence = exec_sequence_individual
                vm_size_individual.Individual_allocation_policy = allocation_policy_individual

            fits = self.toolbox.map(self.toolbox.evaluate, vm_size_offspring)

            # offspring is a list of individuals and fits is a list of fitnesses ()

            for fit, ind_vm_size, ind_sequence, ind_allocation_policy in zip(fits, vm_size_offspring,
                                                                                              exec_sequence_offspring,
                                                                                              allocation_policy_offspring):
                individual_index = vm_size_offspring.index(ind_vm_size)
                key = individual_index + (gen * self.pop_size)
                # ExecTime: when the last cloudlet finish execution
                self.ExecTime = fit[0]
                self.TotalPower = fit[1]
                self.TotalCost = fit[2]
                self.NumberofSLAviolations = fit[3]

                self.normalized_fitness = self.normalize_results_minMax(fit)

                if len(self.weighted_sum) != 0:
                    self.tensor_fitness = self.normalized_fitness
                    self.objective_dict[key] = [self.ExecTime, self.TotalPower, self.TotalCost,
                                                self.NumberofSLAviolations,
                                                self.tensor_fitness]
                    ind_vm_size.fitness.values = self.normalized_fitness,
                    ind_sequence.fitness.values = self.normalized_fitness,
                    ind_allocation_policy.fitness.values = self.normalized_fitness,
                else:
                    self.tensor_fitness = sum(self.normalized_fitness) * 10
                    self.objective_dict[key] = [self.ExecTime, self.TotalPower, self.TotalCost,
                                                self.NumberofSLAviolations,
                                                self.tensor_fitness]
                    ind_vm_size.fitness.values = self.normalized_fitness
                    ind_sequence.fitness.values = self.normalized_fitness
                    ind_allocation_policy.fitness.values = self.normalized_fitness

            self.pareto_front.update(vm_size_population)


            if self.solution_technique == 'Metaheuristic_GA':
                vm_size_population = self.toolbox.select(vm_size_offspring, self.pop_size)
                exec_sequence_population = self.toolbox.select(exec_sequence_offspring, self.pop_size)
                allocation_policy_population = self.toolbox.select(allocation_policy_offspring, self.pop_size)

            else:
                vm_size_population = self.toolbox.select(vm_size_population + vm_size_offspring, self.pop_size)
                exec_sequence_population = self.toolbox.select(exec_sequence_population + exec_sequence_offspring,
                                                               self.pop_size)
                allocation_policy_population = self.toolbox.select(
                    allocation_policy_population + allocation_policy_offspring, self.pop_size)

        print('\n##### Computational time of the optimization:', (timeit.default_timer() - self.start) / 60,
              'minutes #####')
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


def SuffleM(M):
    shuffled = random.sample(M, len(M))
    return shuffled


# Number of vm adaptation
def VmAllocation(self):
    vmNumber = self
    vmTuple = []
    for i in (1, 2, 3):
        if i == 1:
            RandvmCnt = random.randrange(vmNumber)
            newvmNumber = vmNumber - RandvmCnt
            vmTuple.append([i, RandvmCnt])
        elif i == 2:
            newRandvmCnt = random.randrange(newvmNumber)
            vmTuple.append([i, newRandvmCnt])
        elif i == 3:
            treenewvmNumber = vmNumber - (RandvmCnt + newRandvmCnt)
            vmTuple.append([i, treenewvmNumber])
        else:
            print("invalid vm Size")
    print("vm Tuple: ", vmTuple)
    return vmTuple


def GpuVmAllocation(self):
    vmNumber = self
    gpuvmTuple = []
    for i in (1, 2, 3):
        if i == 1:
            RandvmCnt = random.randrange(vmNumber)
            newvmNumber = vmNumber - RandvmCnt
            gpuvmTuple.append([i, RandvmCnt])
        elif i == 2:
            newRandvmCnt = random.randrange(newvmNumber)
            gpuvmTuple.append([i, newRandvmCnt])
        elif i == 3:
            treenewvmNumber = vmNumber - (RandvmCnt + newRandvmCnt)
            gpuvmTuple.append([i, treenewvmNumber])
        else:
            print("invalid vm Size")
    print("Gpuvm Tuple: ", gpuvmTuple)
    return gpuvmTuple


# Number of hosts adaptation
def HostAllocation(self):
    vmNumber = self
    hostTuple = []
    for i in (1, 2, 3):
        RandHost = random.randrange(int(vmNumber / 2), vmNumber)
        hostTuple.append([i, RandHost])
    print("host Tuple: ", hostTuple)
    return hostTuple


def GpuHostAllocation(self):
    gpuvmNumber = self
    gpuhostTuple = []
    for i in (1, 2, 3):
        RandHost = random.randrange(int(gpuvmNumber / 2), gpuvmNumber)
        gpuhostTuple.append([i, RandHost])
    print("Gpuhost Tuple: ", gpuhostTuple)
    return gpuhostTuple