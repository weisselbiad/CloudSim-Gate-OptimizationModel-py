import timeit
from simulation_model.simulation_model import SimulationModel
from execution.problem_instance import Problem_instance


class Evaluation():

    # TODO: Finish initialization method
    def __init__(self, solution_technique, results_logger):

        self.solution_technique = solution_technique
        self.results_logger = results_logger

    def evalFitness(self, initial_problem, num_machines, individual):

        # create model instance and run simulation
        n_machines_s1 = num_machines

        allocation_map = list(individual)
        problem_instance = Problem_instance.ga_allocation(initial_problem, allocation_map)

        simulationModel = SimulationModel(problem_instance=problem_instance,
                                          n_machines_s1=n_machines_s1,
                                          solution_technique=self.solution_technique,
                                          results_logger=self.results_logger,
                                          tracing=False)

        return simulationModel.total_tardiness, simulationModel.makespan, \
               simulationModel.n_penalties, simulationModel.n_major_setups_s1

    def evalBestSolutions(self, initial_problem, individual, individual_index, num_machines):

        # create model instance and run simulation
        n_machines_s1 = num_machines

        allocation_map = list(individual)
        problem_instance = Problem_instance.ga_allocation(initial_problem, allocation_map)

        simulationModel = SimulationModel(problem_instance=problem_instance,
                                          n_machines_s1=n_machines_s1,
                                          solution_technique=self.solution_technique,
                                          results_logger=self.results_logger,
                                          tracing=False)


        if self.results_logger.level == 2:
            simulationModel.log_results(individual_index)

        return (simulationModel.total_tardiness, simulationModel.makespan, simulationModel.n_penalties,
                simulationModel.n_major_setups_s1)
