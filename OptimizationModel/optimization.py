import os
import timeit
import random
import time
import tensorflow as tf
import multiprocessing
from datetime import datetime
from pathlib import Path
from deap import base, creator, tools, algorithms
from py4j.java_gateway import JavaGateway, CallbackServerParameters

from OptimizationModel.evaluation import Evaluation


class Optimization:

    NOBJ = 0
    def __init__(self, pop_size, num_generations, solution_technique, multi_processing, weighted_sum,
                 tensorboard,VmCnt, VmSize):

        gateway = JavaGateway(callback_server_parameters=CallbackServerParameters())
        
        self.gateway = gateway
        self.weighted_sum = weighted_sum
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.cxpb = 0.2
        self.mutpb = 0.1
        self.solution_technique = solution_technique
        #self.results_logger = results_logger
        self.tensorboard = tensorboard
        self.multi_processing = multi_processing
        self.toolbox = base.Toolbox()
        self.pareto_dict = {}

        #self.VmSize = VmSize
        self.VmCnt = VmCnt
        self.VmSize = VmSize
        #self.hostSize = hostSize
        if multi_processing:
            mgr = multiprocessing.Manager()
            self.objective_dict = mgr.dict()
            pool_size = multiprocessing.cpu_count()
            print('Number of CPU cores', pool_size)
            self.pool = multiprocessing.Pool(processes=pool_size)
            self.toolbox.register("map", self.pool.map)

        else:
            self.objective_dict = {}

        if len(self.weighted_sum) != 0:
            self.pareto_front = tools.HallOfFame(30)
        else:
            self.pareto_front = tools.ParetoFront()


        if self.tensorboard:
            local_dir = os.getcwd()
            local_dir = os.path.join(local_dir, 'results_tensorboard')
            tb_out_dir = Path(f'{local_dir}\\{solution_technique, datetime.now().strftime("%b_%d_%Y_%H-%M-%S-fff")}')
            self.writer = tf.summary.create_file_writer(str(tb_out_dir))

        self.evaluation_instance = Evaluation(self.gateway)
        #instead of evalFitness pass an interface to the Simulation in JAVA
        #register on the interface that you will create a method that will invoke the java code based
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

        random.seed(time.process_time())
#        family_types = self.initial_problem['Family type (SMD)'].drop_duplicates().tolist()
        #we define the range of taken number of machines
       # self.toolbox.register("smd_allocation", random.randint, 1, self.VmSize)
        self.toolbox.register("VmCnt_allocation", random.randint, 1, self.VmCnt)
        self.toolbox.register("vmtype_allocation", random.randint, 1, self.VmSize)
        #self.toolbox.register("hosttype_allocation", random.randint, 1, self.hostSize)

        self.toolbox.register("individual", tools.initCycle, creator.Individual_allocation, (self.toolbox.VmCnt_allocation,self.toolbox.vmtype_allocation,),n=1)
        #                      n=len(family_types))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxUniform, indpb=0.9)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.5)
        self.toolbox.register("select", tools.selTournament, tournsize=10)


    def NSGA3(self):

        # TODO: check if I should generate a random seed or it is directly handled by random package
        P = 3
        random.seed(time.process_time())
#        family_types = self.initial_problem['Family type (SMD)'].drop_duplicates().tolist()
        self.toolbox.register("smd_allocation", random.randint, 0, self.VmCnt-1)
        self.toolbox.register("vmtype_allocation", random.randint, 0, self.VmSize-1)
        self.toolbox.register("individual", tools.initCycle, creator.Individual_allocation, (self.toolbox.smd_allocation,self.toolbox.vmtype_allocation),
                              n=2)#len(family_types))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxUniform, indpb=self.cxpb)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=self.mutpb)
        self.ref_points = tools.uniform_reference_points(Optimization.NOBJ, P)
        self.toolbox.register("select", tools.selNSGA3, ref_points=self.ref_points)

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

                if self.tensorboard:
                    self.activate_tensorboard()

            self.pareto_front.update(population)

            if self.solution_technique == 'Metaheuristic_NSGA3':
                population = self.toolbox.select(population + offspring, self.pop_size)
            else:
                population = self.toolbox.select(offspring, self.pop_size)

        if self.multi_processing:
            self.pool.close()

        print('\n##### Computational time of the optimization:', (timeit.default_timer() - self.start) / 60,
              'minutes #####')
        print('-------------------------------------------------------------------------------')

   #     self.log_results()

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

    def activate_tensorboard(self):

        with self.writer.as_default():
            tf.summary.scalar(name='Fitness', data=self.tensor_fitness, step=len(self.objective_dict))
            tf.summary.scalar(name='ExecTime', data=self.ExecTime, step=len(self.objective_dict))
            tf.summary.scalar(name=' Total Power', data=self.TotalPower, step=len(self.objective_dict))
            self.writer.flush()

    def log_results(self):

        for i in range(len(self.pareto_front)):
            individual = self.pareto_front[i]
            original_objective_values = self.evaluation_instance.evalBestSolutions(self.initial_problem, individual, i, self.VmSize)
            self.pareto_dict[i] = [original_objective_values, individual.fitness.values]

        pareto_list = list(self.pareto_dict.values())
        self.results_logger.write_pareto_front_to_csv(pareto_list)
        del self.pareto_dict

        if self.multi_processing:
            self.pool.close()

        if self.results_logger.level is not None:
            objective_values = list(self.objective_dict.values())
            self.results_logger.write_KPIs_to_csv(objective_values, '')  # TODO: pass the optimization run number

        del self.objective_dict

