import argparse
import random
from typing import NamedTuple, Union

from py4j.java_gateway import JavaGateway, CallbackServerParameters, GatewayParameters

from OptimizationModel.optimization import Optimization

from execution.results_writer import Results_writer
import os
from pathlib import Path
from datetime import datetime
from deap import base, creator, tools, algorithms


# TODO: write a method for testing and validation (single-run)

class ExperimentConfig(NamedTuple):

    results_dir: Union[None, Path]
    nojb: int
    generations: int
    population: int

def main(exp_config: ExperimentConfig):

    num_optimization_runs = 3
    problem = '1'
    # if exp_config.results_dir is None:
    #     local_dir = os.getcwd()
    #     local_dir = Path(local_dir).joinpath('results_csv').joinpath(
    #         problem + '_problem_' + datetime.now().strftime("%b_%d_%Y_%H-%M-%S"))
    #     local_dir.mkdir(parents=True)
    # else:
    #     local_dir = exp_config.results_dir
    def generateSetup():
        r = 200
        M = []
        for i in range(r):
            P = []
            for j in range(1):
                Size = random.randint(1, 3)
                Seq = random.randint(1, 6)
                allocationpolicy = random.randint(1, 3)
                P.append(Size)
                P.append(Seq)
                P.append(allocationpolicy)
            M.append(P)
        return M

    gateway = JavaGateway(callback_server_parameters=CallbackServerParameters(daemonize=True,
                                                                              daemonize_connections=True,
                                                                              accept_timeout=160,
                                                                              propagate_java_exceptions=True),
                          gateway_parameters=GatewayParameters(auto_close=True))
    gateway.restart_callback_server()
    for i in range(num_optimization_runs):
        logging_level = 1
        solution_technique = 'Metaheuristic_GA'  # Metaheuristic_NSGA3, Metaheuristic_GA
        # Shape: [normalizedTardiness, normalizedTardiness, normalizedPenalties, normalizedMajorSetup]
        initSetup = generateSetup()

        weighted_sum = []  # [20, 30, 30 * (100), 20]
        pop_size = exp_config.population
        num_generations = exp_config.generations
        Optimization.NOBJ = exp_config.nojb
        Optimization(pop_size, num_generations, solution_technique, weighted_sum, gateway=gateway)
        print('\n#################################### Optimization run', i, 'is finished ####################################\n')

NOBJ = 2
creator.create("FitnessMin", base.Fitness, weights=(-1.0,) * NOBJ)
creator.create("Individual_vm_size", list, fitness=creator.FitnessMin, Individual_exec_sequence=None, Individual_allocation_policy=None)
creator.create("Individual_exec_sequence", list, fitness=creator.FitnessMin)
creator.create("Individual_allocation_policy", list, fitness=creator.FitnessMin)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--result-dir',
                        help='Results dir. If not specified, using default.',
                        required=False,
                        type=str,
                        default=None)
    parser.add_argument('--nojb',
                        help='NOJB',
                        required=False,
                        type=int,
                        default=NOBJ)
    parser.add_argument('-g', '--generations',
                        help='Number of generations.',
                        required=False,
                        type=int,
                        default=3)
    parser.add_argument('-p', '--population',
                        help='Population size.',
                        required=False,
                        type=int,
                        default=10)

    config_parsed = parser.parse_args()
    out_path = None

    if config_parsed.result_dir is not None:
        out_path = Path(config_parsed.result_dir)

    exp_config = ExperimentConfig(out_path,
                                  config_parsed.nojb,
                                  config_parsed.generations,
                                  config_parsed.population)

    main(exp_config)