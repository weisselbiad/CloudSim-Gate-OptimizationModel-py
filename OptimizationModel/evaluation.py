# TODO: Finish this method to send the solution individual suggested by the optimization to the simulation model
"""
Here how you will pase every individual and split them into vm_size_individual, exec_sequence_individual,
allocation_policy_individual before sending it to the simulation side
:param vm_size_individual:
:return:
vm_size_individual = list(vm_size_individual)
exec_sequence_individual = list(vm_size_individual.Individual_exec_sequence)
allocation_policy_individual = list(vm_size_individual.Individual_allocation_policy)
You integration down seemn to be wrong, you have to pass the solution individuals in the previous shape
"""
import timeit
from py4j.java_gateway import JavaGateway, CallbackServerParameters
import json
import os

# Class Listener define for the py4j gateway
class Listener (object):
    def __init__(self, gateway):
     self.gateway = gateway
     self.FilePath = ''
    def setFilePath(self, obj):
        self.FilePath = obj

    def returnSize(size):
            switch = {
                1: "S",
                2: "M",
                3: "L"
            }
            return switch.get(size, "Invalid input")

    # notify json file path
    def notifyFilePath(self, obj):
        return self.FilePath

    # Implement the Listener interface from java
    class Java:
        implements = ["pl.edu.agh.csg.Listener"]


class Evaluation():
    def __init__(self, *args):
     self.gateway = args[0]
     self.Jobset =args[1]
    def getJobdet(self):
        return self.Jobset
        # function defined as an interface to the Simulation
    def evalBridge(self,  vm_size_individual: tuple):



      # split the results to VM and Hosts Parameters

       vm_size_individual = vm_size_individual
       exec_sequence_individual = vm_size_individual.Individual_exec_sequence
       allocation_policy_individual = vm_size_individual.Individual_allocation_policy

       results = []
       for i in range(len(vm_size_individual)):
        results.append([vm_size_individual[i],exec_sequence_individual[i],allocation_policy_individual[i]])

       print(results)
       def writeAjson(file, data):
           with open(file, 'w') as fp:
               json.dump(data, fp)

       dict ={
        "Indiv" : results
       }
       file = 'resultes.json'

       writeAjson(file, dict)

       # run methodes using the gateway to CloudSimPlus
       listener = Listener(self.gateway)
       ListenerJava = self.gateway.entry_point.getListenerApp()

       listener.setFilePath(os.path.abspath(file))
       ListenerJava.notifyFilePath(listener)

       ListenerJava.Init(Evaluation.getJobdet(self))
       # run simulation
       S = self.gateway.entry_point.getsimulation()
       S.runSim()
       #get and print results
       ExecTime = S.getVmCost()[-1]
       TotalPower = S.getPowerConsumption()
       TotalCost = S.getVmCost()[-2]
       NumberofSLAviolations= S.getNumofSLAviolation()

       print("Solutions: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< \n")
       for i in range(len(results)):
        print (" \n"
              ,"     Virtual Machine  ",i,"    \n "
              ,"Size: ",results[i][0],"\n"
              ,"Sequence: ", results[i][1], "\n"
              , "Allocation Policy: ", results[i][2],"\n"
              )
       print("ExecTime: ", ExecTime," ms || ", "TotalPower: ", TotalPower," watts || ", "TotalCost: ",TotalCost," $ || ","NumberofSLAviolations: ",NumberofSLAviolations," \n")

       return ExecTime, TotalPower, TotalCost, NumberofSLAviolations