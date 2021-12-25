import timeit
from py4j.java_gateway import JavaGateway, CallbackServerParameters



class Listener (object):
    def __init__(self, gateway):
     self.gateway = gateway
     self.hostCnt = 0
     self.VmSize = 0
     self.VmCnt = 0
     self.hostSize = 0

    def sethostCnt(self, hC):
        self.hostCnt = hC

    def sethostSize (self, hS):
        self.hostSize = hS

    def setVmCnt(self,VC):
        self.VmCnt =  VC

    def setVmSize(self, VS):
       self.VmSize = VS

    def returnSize(size):
            switch = {
                1: "S",
                2: "M",
                3: "L"
            }
            return switch.get(size, "Invalid input")

    def getVmType(self):
       if  self == 0:
          varVmType = Listener.returnSize(1)

       else:
          varVmType = Listener.returnSize(self)

       return varVmType

    def gethostType(self):
       if  self == 0:
          varhostType = Listener.returnSize(1)

       else:
          varhostType = Listener.returnSize(self)

       return varhostType


    def notifyVmSize(self, obj):
     VmType = Listener.getVmType(self.VmSize)
     return VmType

    def notifyhostType (self, obj):
        hostType = Listener.gethostType(self.hostSize)
        return hostType

    def notifyHost(self, obj):
       if self.hostCnt == 0:
          self.hostCnt = 10
          return self.hostCnt
       else:
          return self.hostCnt

    def notifyVmCnt(self,obj):
        if self.VmCnt == 0:
            self.VmCnt = 20
            return self.VmCnt
        else:
            return self.VmCnt

        # Implement the Listener interface from java

    class Java:
        implements = ["pl.edu.agh.csg.Listener"]


class Evaluation():
    def __init__(self, gateway):
     self.gateway = gateway


    def evalBridge(self, results):
       vmCnt = results[0]

       def vmSize ():
           if results[1] > 3:
               vmSize = 3
               return vmSize
           elif results[1]<1:
               vmSize = 1
               return vmSize
           else:
               vmSize = results[1]
               return vmSize

       def hostSize ():
           if results[1] > 3:
               hostSize = 3
               return hostSize
           elif results[1] < 1:
               hostSize = 1
               return hostSize
           else:
               hostSize = results[1]
               return hostSize

       listener = Listener(self.gateway)

       def setHostCnt(vmSize):
           vmSize = vmSize()

           if vmSize ==1:
             hostCnt = int(vmCnt / 12)+1
             return hostCnt
           elif vmSize == 2:
             hostCnt = int(vmCnt / 6)+1
             return hostCnt
           elif vmSize == 3:
             hostCnt = int(vmCnt / 3)+1
             return hostCnt
           else:
               print("Invalid Vm Size")

       HostCnt = setHostCnt(vmSize)
       listener.sethostCnt(HostCnt)
       listener.setVmCnt(vmCnt)
       listener.setVmSize(vmSize)

       ListenerJava = self.gateway.entry_point.getListenerApp()
       ListenerJava.notifyVmCnt(listener)
       ListenerJava.notifyVmType(listener)
       ListenerJava.notifyhostCnt(listener)
       ListenerJava.Init()

       S = self.gateway.entry_point.getsimulation()
       S.runSim()

       ExecTime = S.getVmCost()[-1]
       TotalPower = S.getPowerConsumption()
       TotalCost = S.getVmCost()[-2]
       print("num of hosts: ",HostCnt, "num of Vms: ",vmCnt)
       print ("Sol: >>>>>   ",results)
       print("ExecTime: ", ExecTime, "TotalPower: ", TotalPower, "TotalCost: ",TotalCost)

       return ExecTime, TotalPower, TotalCost



'''
    # TODO: Finish initialization method
    def __init__(self, solution_technique, results_logger):

        self.solution_technique = solution_technique
        self.results_logger = results_logger



    def evalFitness(self, initial_problem, num_machines, individual, S):

        # create model instance and run simulation
        n_machines_s1 = num_machines

        allocation_map = list(individual)
        problem_instance = Problem_instance.ga_allocation(initial_problem, allocation_map)

        self.S.runSim()
        CloudletsList = S.getCloudletlist()
        length = len(CloudletsList)
        total_tardiness = CloudletsList.getWaitTime()[1]*length
        ExecTime = S.getVmCost()[2]
        n_penalties = S.getVmCost()[1]
        n_major_setups_s1 = 0

        return total_tardiness, ExecTime , \
               n_penalties, n_major_setups_s1

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

        simulationModel.print_results()
        return (simulationModel.total_tardiness, simulationModel.ExecTime, simulationModel.n_penalties,
                simulationModel.n_major_setups_s1)
'''