import json
from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
S = gateway.entry_point.getsimulation()
file = "test.json"

CloudletsList = S.getInputJobs()
length = len(CloudletsList)

def write_json(data, filename="test.json"):
    with open(filename, "w") as f:
        json.dump(data, f)


with open(file, "r") as json_file:
    data = []
    for i in range(length):
        data.append("VM Id: ")
        data.append(CloudletsList[i].getVm().getId())
write_json(data)

