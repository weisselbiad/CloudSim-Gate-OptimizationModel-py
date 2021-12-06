from py4j.java_gateway import JavaGateway, CallbackServerParameters

"""
Initializing the gateway and passing CallbackSeverParameters to be able to implement java interfaces 
it could be intialized without CallbackServer but the communication would be just in one direction
"""

gateway = JavaGateway(callback_server_parameters=CallbackServerParameters())

"""
Create Class Python Listener and define constructor
Create Methode which notify the Java Class ListenerApp
"""

class PythonListener(object):
    def __init__(self, gateway):
        self.gateway = gateway

    def returnSize(size):
        switch={
            1:"S",
            2:"M",
            3:"L"
            }
        return switch.get(size,"Invalid input")

    Size = 2
    varVmType = returnSize(Size)
    varhostCnt = 10

    def notifyVm(self, obj):
        #gateway.jvm.System.out.println("Hello from python!, VmType: ", self.varVmType)
        return self.varVmType

    def notifyHost(self, obj):
        #gateway.jvm.System.out.println("Hello from python!, Number of Hosts: ",self.varhostCnt)
        return self.varhostCnt

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
    L.notifyVmType(listener)
    L.notifyhostCnt(listener)
#    L.getReturnValue()
    L.Init()
    S = gateway.entry_point.getsimulation()
    S.runSim()
#    gateway.shutdown()
