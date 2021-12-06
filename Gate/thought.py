"""
getting the simulation which is defined in the java main class
running the simulation
"""



"""
"""

"""
get Cloudlets List in order to print or get Simulation settings
CloudletsList = S.getCloudletlist()
length = len(CloudletsList)

for i in range(length):
    print(CloudletsList[i].getId ,CloudletsList[i].getStatus().name())
    print("DC Id: ",CloudletsList[i].getVm().getHost().getDatacenter().getId())
    print("Host Id: ",CloudletsList[i].getVm().getHost().getId()," PEs: ",CloudletsList[i].getVm().getHost().getWorkingPesNumber())
    print("VM Id: ",CloudletsList[i].getVm().getId()," PEs: ",CloudletsList[i].getVm().getNumberOfPes(), CloudletsList[i].getVm().getStorage())
    print("CloudletPes:",CloudletsList[i].getNumberOfPes())

"""

"""
Writing data on a Json file
def writeAjson(file, data):
    with open(file, 'w') as fp:
        json.dump(data, fp)

"""

"""
Prepare dictionary for Json

file = 'Ids.json'
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

file2 = 'Settings.json'
Settings = gateway.entry_point.getSimSettings()
writeAjson(file2, Settings.toString())

"""