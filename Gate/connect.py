import json
from py4j.java_gateway import JavaGateway, CallbackServerParameters

"""
Initializing the gateway and passing CallbackSeverParameters to be able to implement java interfaces 
it could be intialized without CallbackServer but the communication would be just in one direction
"""

gateway = JavaGateway(callback_server_parameters=CallbackServerParameters())

"""
getting the simulation which is defined in the java main class 
running the simulation
"""

S = gateway.entry_point.getsimulation()
S.runSim()

"""
get Cloudlets List in order to print or get Simulation settings
"""

CloudletsList = S.getCloudletlist()
length = len(CloudletsList)

for i in range(length):
    print(CloudletsList[i].getId,CloudletsList[i].getStatus().name())
    print("DC Id: ",CloudletsList[i].getVm().getHost().getDatacenter().getId())
    print("Host Id: ",CloudletsList[i].getVm().getHost().getId()," PEs: ",CloudletsList[i].getVm().getHost().getWorkingPesNumber(), " Storage: ",CloudletsList[i].getVm().getHost().getAvailableStorage())
    print("VM Id: ",CloudletsList[i].getVm().getId()," PEs: ",CloudletsList[i].getVm().getNumberOfPes(), CloudletsList[i].getVm().getStorage())

"""
Writing data on a Json file
"""

def writeAjson(file, data):
    with open(file, 'w') as fp:
        json.dump(data, fp)

"""
Prepare dictionary for Json
"""

file = 'test.json'
def createDct():
    data_list = []
    print(length)
    for i in range(length):
        data = {}
        data['DC Id'] = CloudletsList[i].getVm().getHost().getDatacenter().getId()
        data['Host Id'] = CloudletsList[i].getVm().getHost().getId()
        data['vm Id'] = CloudletsList[i].getVm().getId()

        data_list.append(data)

    return data_list

finalData = createDct()
writeAjson(file, finalData)

"""
Create Class Python Listener and define constructor
Create Methode which notify the Java Class ListenerApp
"""

class PythonListener(object):

    def __init__(self, gateway):
        self.gateway = gateway

    def notify(self, obj):
        print("Notified by Java")
        print(obj)
        gateway.jvm.System.out.println("Hello from python!, here the submitted Id list: ")
        return repr(finalData)
#Implement the Listener interface from java

    class Java:
        implements = ["pl.edu.agh.csg.Listener"]


'''
Pass the gateway as parameter of PythonListener
The whole Object will be put as parameter of registerListener() which is a methode of 
ListenerApp on Java
'''

if __name__ == "__main__":
    listener = PythonListener(gateway)
    L = gateway.entry_point.getListenerApp()
    L.registerListener(listener)
    L.notifyAllListeners()
    gateway.shutdown()
