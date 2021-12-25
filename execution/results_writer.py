import csv
import os
from pathlib import Path
class Results_writer():

    def __init__(self, level, solution_technique: str, num_optimization_runs: int, dir):


        # TODO: self.logging_type = logging_type ---> csv, datastream, ..
        self.num_optimization_runs = num_optimization_runs
        self.solution_technique = solution_technique
        self.level = level
        self.local_dir = dir
        self.log_names = []
        self.level_names = ['_KPIs', '_Detailed_schedule']

        if self.level < 3:
            for i in range(self.level):
                name = self.level_names[i]
                log_name = (str(self.num_optimization_runs) + solution_technique + name)
                self.log_names.append(log_name)
        else:
            print(
                '\n## logging error ## \n-Two logging levels are available: 1 for KPIs and 2 for detailed \n-Note: '
                'The naming is case-sensitive')

    def write_KPIs_to_csv(self, results, solution_index):

        if len(self.log_names) < 3:
            log_name = self.log_names[0]
            log_name = (log_name + solution_index + '.csv')
            csv_path = self.local_dir.joinpath(log_name)
            csv_file = open(csv_path, mode='w', newline="")
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(results)
            csv_file.close()
        else:
            print(
                '\n## logging error ## \n-Two logging levels are available: 1 for KPIs and 2 for detailed \n-Note: '
                'The naming is case-sensitive')

    def write_pareto_front_to_csv(self, pareto_front):

        #print(pareto_front)
        name = '_Pareto_front'
        log_name = (str(self.num_optimization_runs) + self.solution_technique + name)
        log_name = (log_name + '.csv')
        csv_path = self.local_dir.joinpath(log_name)
        csv_file = open(csv_path, mode='w', newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(pareto_front)
        csv_file.close()

    def write_detailed_to_csv(self, results, solution_index):

        if len(self.log_names) > 1:
            log_name = self.log_names[1]
            log_name = (log_name + solution_index + '.csv')
            csv_path = self.local_dir.joinpath(log_name)
            csv_file = open(csv_path, mode='w', newline="")
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(results)
            csv_file.close()
        else:
            print(
                '\n## logging error ## \n-logging detailed schedule with insufficient logging level \n')
