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
    def __init__(self, gateway):
     self.gateway = gateway

    # function defined as an interface to the Simulation
    def evalBridge(self,  results):
      # split the results to VM and Hosts Parameters
       vmTuple = results[0]
       hostTuple = results[1]

      # prepare a json file
       def writeAjson(file, data):
           with open(file, 'w') as fp:
               json.dump(data, fp)

       dict ={
           "Vm" : vmTuple,
           "Host" : hostTuple
       }
       file = 'resultes.json'

       writeAjson(file, dict)

       # run methodes using the gateway to CloudSimPlus
       listener = Listener(self.gateway)
       ListenerJava = self.gateway.entry_point.getListenerApp()

       listener.setFilePath(os.path.abspath(file))
       ListenerJava.notifyFilePath(listener)

       ListenerJava.Init()
       # run simulation
       S = self.gateway.entry_point.getsimulation()
       S.runSim()
       #get and print results
       ExecTime = S.getVmCost()[-1]
       TotalPower = S.getPowerConsumption()
       TotalCost = S.getVmCost()[-2]


       print ("Solutions: >>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<< \n"
              ,"     Virtual Machines              Physical Machines\n "
              ,"Size: ",vmTuple[0][0],"                          Size: ",hostTuple[0][0],"\n"
              ,"Number of Vms: ", vmTuple[0][1], "                Number of Hosts: ", hostTuple[0][1], "\n"
              , "Size: ", vmTuple[1][0], "                          Size: ", hostTuple[1][0], "\n"
              ,"Number of Vms: ", vmTuple[1][1], "                Number of Hosts: ", hostTuple[1][1], "\n"
              , "Size: ", vmTuple[2][0], "                           Size: ", hostTuple[2][0], "\n"
              ,"Number of Vms: ", vmTuple[2][1], "               Number of Hosts: ", hostTuple[2][1], "\n"

              )
       print("ExecTime: ", ExecTime," ms || ", "TotalPower: ", TotalPower," watts || ", "TotalCost: ",TotalCost," $ \n")

       return ExecTime, TotalPower, TotalCost

