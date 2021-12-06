import os
import timeit
import random
import time
import tensorflow as tf
import multiprocessing
from datetime import datetime
from pathlib import Path
from deap import base, creator, tools, algorithms
from evaluation import Evaluation


class Optimization:

    NOBJ = 0
    def __init__(self, initial_problem, pop_size, num_generations, solution_technique, multi_processing, weighted_sum,
                 results_logger, tensorboard, num_machines):

        self.weighted_sum = weighted_sum
        self.initial_problem = initial_problem
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.cxpb = 0.7
        self.mutpb = 0.5
        self.solution_technique = solution_technique
        self.results_logger = results_logger
        self.tensorboard = tensorboard
        self.multi_processing = multi_processing
        self.toolbox = base.Toolbox()
        self.pareto_dict = {}
        self.num_machines = num_machines
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

        self.evaluation_instance = Evaluation('Metaheuristic', self.results_logger)
        self.toolbox.register("evaluate", self.evaluation_instance.evalFitness, self.initial_problem, self.num_machines)

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
        family_types = self.initial_problem['Family type (SMD)'].drop_duplicates().tolist()
        self.toolbox.register("smd_allocation", random.randint, 0, self.num_machines-1)
        self.toolbox.register("individual", tools.initCycle, creator.Individual_allocation, (self.toolbox.smd_allocation,),
                              n=len(family_types))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxUniform, indpb=0.9)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.7)
        self.toolbox.register("select", tools.selTournament, tournsize=10)


    def NSGA3(self):

        # TODO: check if I should generate a random seed or it is directly handled by random package
        P = 3
        random.seed(time.process_time())
        family_types = self.initial_problem['Family type (SMD)'].drop_duplicates().tolist()
        self.toolbox.register("smd_allocation", random.randint, 0, self.num_machines-1)
        self.toolbox.register("individual", tools.initCycle, creator.Individual_allocation, (self.toolbox.smd_allocation,), n=len(family_types))
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
            for fit, ind in zip(fits, offspring):
                individual_index = offspring.index(ind)
                key = individual_index + (gen * self.pop_size)
                self.total_tardiness = fit[0]
                self.makespan = fit[1]
                self.penalties = fit[2]
                self.major_setup_s1 = fit[3]

                self.normalized_fitness = self.normalize_results_minMax(fit)
                if len(self.weighted_sum) != 0:
                    self.tensor_fitness = self.normalized_fitness
                    self.objective_dict[key] = [self.makespan, self.total_tardiness,
                                                self.penalties, self.major_setup_s1,
                                                self.tensor_fitness]
                    ind.fitness.values = self.normalized_fitness,
                else:
                    self.tensor_fitness = sum(self.normalized_fitness) * 10
                    self.objective_dict[key] = [self.makespan, self.total_tardiness,
                                                self.penalties, self.major_setup_s1,
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

        self.log_results()

    def normalize_results_minMax(self, fitness):

        ### Normalization ########################################################################

        makespan = fitness[1]  # Makespan
        makespanMin = 12000
        makespanMax = 14000

        if makespanMax - makespanMin == 0:
            normalizedMakespan = 1
        else:
            normalizedMakespan = (makespan - makespanMin) / (makespanMax - makespanMin)

        tardiness = fitness[0]  # Total tardiness
        tardinessMin = 0
        tadinessMax = 1000

        if tadinessMax - tardinessMin == 0:
            normalizedTardiness = 1
        else:
            normalizedTardiness = (tardiness - tardinessMin) / (tadinessMax - tardinessMin)

        penalties = fitness[2]  # Number of penalties
        penaltiesMin = 0
        penaltiesMax = 5

        if penaltiesMax - penaltiesMin == 0:
            normalizedPenalties = 1
        else:
            normalizedPenalties = (penalties - penaltiesMin) / (penaltiesMax - penaltiesMin)

        majorSetup = fitness[3] # Major Setup
        majorSetupMin = 37
        majorSetupMax = 50

        if majorSetupMax - majorSetupMin == 0:
            normalizedMajorSetup = 1
        else:
            normalizedMajorSetup = (majorSetup - majorSetupMin) / (
                    majorSetupMax - majorSetupMin)

        ### Fittness #############################################################################

        if len(self.weighted_sum) != 0:

            fitness = self.weighted_sum[0] * normalizedMakespan + \
                      self.weighted_sum[1] * normalizedTardiness + \
                      self.weighted_sum[2] * normalizedPenalties + \
                      self.weighted_sum[3] * normalizedMajorSetup
        else:
            fitness = (normalizedTardiness, normalizedMakespan, normalizedPenalties, normalizedMajorSetup)

        return fitness

    def activate_tensorboard(self):

        with self.writer.as_default():
            tf.summary.scalar(name='Fitness', data=self.tensor_fitness, step=len(self.objective_dict))
            tf.summary.scalar(name='Makespan', data=self.makespan, step=len(self.objective_dict))
            tf.summary.scalar(name='Major Setups of the first stage', data=self.major_setup_s1,
                              step=len(self.objective_dict))
            tf.summary.scalar(name=' Total Tardiness', data=self.total_tardiness, step=len(self.objective_dict))
            tf.summary.scalar(name='Penalties', data=self.penalties, step=len(self.objective_dict))
            self.writer.flush()

    def log_results(self):

        for i in range(len(self.pareto_front)):
            individual = self.pareto_front[i]
            original_objective_values = self.evaluation_instance.evalBestSolutions(self.initial_problem, individual, i, self.num_machines)
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

