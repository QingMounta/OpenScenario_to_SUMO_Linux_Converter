from multiprocessing.connection import Client
from pickle import TRUE
import socket
import time
import threading
import random
import os, sys
from turtle import width
import traci
import traci.constants as tc
import json
import sumolib
import csv
import pandas as pd


class SocketServerSimple:
    HOST = "127.0.0.1"
    PORT = 25001

    messageToSend = ""
    messageReceived = ""
    messageSize = 1024

    delta = 0.5
    nrOfConnection = 0
    conn = ""
    def __init__(self, ip="127.0.0.1", port=25001, delta=0.015, nrListeners=1, messageSize=1024):
        self.PORT = port
        self.HOST = ip
        self.delta = delta
        self.nrListeners = nrListeners
        self.messageSize = messageSize

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.HOST,self.PORT))

        sock.listen(self.nrListeners)
        conn, address = sock.accept()
        self.conn = conn
        print("Connection from: " + str(address))
        
        while True:
            # Send Data
            conn.sendall(self.messageToSend.encode("UTF-8"))

            # Receive Data
            receivedData = conn.recv(1024).decode("UTF-8")
            self.messageReceived = receivedData
            if(receivedData is not None):
                #print(receivedData)
                pass
            time.sleep(self.delta)
        sock.close()

def TraciServer(server,dt):
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")


    traci.start(["sumo-gui","-c", "simulation.sumocfg","--num-clients", "1"])
    traci.setOrder(0)
    step = 0
    while True:
        traci.simulationStep()
        step += 1
        time.sleep(dt)

        
        #print(traci.vehicle.getSubscriptionResults("bike1"))
        
        # ==============================
        # Send Values from SUMO to Unity
        # ==============================
        idList = traci.vehicle.getIDList()
        simulationTime = traci.simulation.getTime()

        vehicleList = list()
        for i in range(0,len(idList)):
            id = idList[i]
            pos = traci.vehicle.getPosition(id)
            rot = traci.vehicle.getAngle(id)
            speed = traci.vehicle.getSpeed(id)
            signals = traci.vehicle.getSignals(id)
            vehType = traci.vehicle.getVehicleClass(id)
            #edge = traci.vehicle.getRoadID(id)
            #length = traci.vehicle.getLength(id)
            #width = traci.vehicle.getWidth(id)

            #print(veh.ToString())
            veh = SumoVehicle(id,pos,rot,speed,signals,vehType)
            vehicleList.append(veh.__dict__)
        
        # Traffic Lights
        tl_id = "C3" # id of the only traffic light in the simulation
        trafficLightPhase = traci.trafficlight.getPhase(tl_id)

        sumoSimStep = SumoSimulationStepInfo(simulationTime,vehicleList,trafficLightPhase).__dict__
        server.messageToSend = json.dumps(sumoSimStep)
        filename = 'SUMO_trafficflow.json'
        with open (filename,'a') as f:
            json.dump(sumoSimStep,f)
            f.write(';')

        

        # ==============================
        # Send Values from Unity to SUMO
        # ==============================
        # Ego Vehicle
        try:
            msg = json.loads(server.messageReceived)
            traci.vehicle.moveToXY(msg["id"],"", 1 ,msg["positionX"],msg["positionY"],msg["rotation"],2)
            #traci.vehicle.setSpeed(msg["id"],msg["speed"])

            
        except:
            pass


        # Exceptions for obstacles
        try:
            # Exceptions for Obstacles
            offsetX = 120
            offsetY = 161.5

            #obst1 = sumoSimStep.getVehicleInfo("obstacle1")
            #obst2 = sumoSimStep.getVehicleInfo("obstacle2") 
            
            traci.vehicle.moveToXY("obstacle1","",1,2 + offsetX,-50 + offsetY,0,2)
            traci.vehicle.moveToXY("obstacle2","",1,-56 + offsetX,-45 + offsetY,180,2)
        except:
            pass
    traci.close()


class SumoVehicle:
    id = ""
    positionX = 0
    positionY = 0
    rotation = 0
    speed = 0
    signals = None
    vehicleType = ""
    def __init__(self, _id, _pos, _rot, _speed, _signals, _vehType):
        self.id = _id
        self.positionX = _pos[0]
        self.positionY = _pos[1]
        self.rotation = _rot
        self.speed = _speed
        self.signals = _signals
        self.vehicleType = _vehType


class SumoSimulationStepInfo:
    time = 0
    trafficLightPhase = 0
    vehicleList = list()      
    #personList = list()

    def __init__(self, _time, _vehicleList, _trafficLightPhase, _personList=list()):
        self.time = _time
        self.vehicleList = _vehicleList
        self.trafficLightPhase = _trafficLightPhase
        #self.personList = _personList

    def getVehicleInfo(self, id):
        for veh in self.vehicleList:
            if veh["id"]==id:
                return veh

class ArduinoInputInfo:
    speed = 0
    steering = 0

    def __init__(self, _speed, _steering):
        self.speed = _speed
        self.steering = _steering

def ArduinoConnection(server, dt):
    ip = '192.168.178.133'
    port = 5000

    
    #Arduino
    address = (ip, port)  # Define who you are talking to (must match arduino IP and port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Set Up the Socket
    client_socket.settimeout(1)  # only wait 1 second for a resonse
    client_socket.sendto("foo".encode("utf-8"), address)  # send command to arduino
    

    while(True):
        time.sleep(dt)
        try:
            client_socket.sendto("foo".encode("utf-8"), address)  # send command to arduino
            rec_data, addr = client_socket.recvfrom(64)  # buffer size is 1024 bytes

            speed, steering = rec_data.decode().split("|")
            server.messageToSend = json.dumps(ArduinoInputInfo(speed,steering).__dict__)
        except:
            pass


def StartSumoGUI():
    traci.start(["sumo-gui", "-c", "circle.sumo.cfg"], port=7911)
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    traci.close()
    sys.exit()

def generateTopology(): 
    AdjacencyList = {}
    for e in net.getEdges():
#   这里判断此条路径是否允许我选择的newVehicleType这个类型的车辆
        
        if e.allows(newVehicletype)==False:
            continue
        if AdjacencyList.__contains__(str(e.getFromNode().getID()))==False:
            AdjacencyList[str(e.getFromNode().getID())]={}
        AdjacencyList[str(e.getFromNode().getID())][str(e.getToNode().getID())] = e.getLanes()[0].getLength()

    return AdjacencyList

def addCar():
# #   edge from
#     ef = "1"
# #   edge to
#     et = "2"
# #   edge set
#     es = generateRoute(ef, et)
#     print(es)
#     traci.route.add(routeID="newRoute", edges="1 2")
    traci.vehicle.add(vehID="newCar")
    traci.vehicle.setVehicleClass(vehID="newCar", clazz="private")
    # traci.vehicle.setEmissionClass(vehID="newCar", clazz="Energy/unknown")
    traci.vehicle.setColor(color=(0,255,0,238), vehID="newCar")
    pass

# def generateRoute(ef, et, INF=float("inf")):
#     return generateMyRoute(ef, et)

# def generateMyRoute(ef, et, INF=float("inf")):
#     nf = str(net.getEdge(ef).getToNode().getID())
#     nt = str(net.getEdge(et).getToNode().getID())
#     print("nf is "+nf+"\nnt is "+nt)
#     nodes = findNodeRoute(nf, nt)
#     edges = []
#     edges.append(ef)
#     s = net.getEdge(ef).getLanes()[0].getLength()
#     for i in range(0,len(nodes)-1):
#         for x in net.getNode(nodes[i]).getOutgoing():
#             if x.getToNode().getID()==nodes[i+1] and x.allows(newVehicletype):
#                 edges.append(x.getID())
#                 s+=x.getLanes()[0].getLength()
#                 break
#     print (len(nodes))
#     print (len(edges))
#     print ("dis is ",s)
#     return edges

# def findNodeRoute(nf, nt, INF=float("inf")):
#     openlist = {}
#     closelist = {}
#     openlist[nf] = [getF(nf, nt, 0), nf]
#     while openlist.__contains__(nt)==False:
#         u = -1
#         minu = INF
#         for x in openlist:
#             if openlist[x][0]<minu :
#                 minu = openlist[x][0]
#                 u = x
#         closelist[u] = openlist[u]
#         del openlist[u]
#         for x in AdjacencyList[u]:

#             if closelist.__contains__(x)==False:
#                 if openlist.__contains__(x)==False:
#                     openlist[x] = [getF(x, nt, closelist[u][0]), u]
# #               print(x+" is added into openlist")
#                 else:
#                     f = getF(x, nt, closelist[u][0])
#                     if f<openlist[x][0]:
#                         openlist[x] = [f, u]
#                 if x==nt:
#                     break
#         if openlist.__contains__(nt):
#             break

# #   backtrace to find the route
#     closelist[nt] = openlist[nt]
#     del openlist[nt]
#     u = nt
#     nodes = []
#     while u!=nf:
#         nodes.insert(0, u)
#         u = closelist[u][1]
#     nodes.insert(0, nf)
#     print ("nodes are", nodes)
#     return nodes
#     pass


# def getF(nf, nt, g):
#     return getAF(nf, nt, g)

# #A* Algoritym, f = h+g
# def getAF(nf, nt, g):
#     nfc = net.getNode(nf).getCoord()
#     nft = net.getNode(nt).getCoord()
#     return pow(pow(nfc[0]-nft[0], 2)+pow(nfc[1]-nft[1], 2), 0.5)+g

# #Greedy Algorithm, Best-First Search, f = h
# def getBF(nf, nt, g):
    nfc = net.getNode(nf).getCoord()
    nft = net.getNode(nt).getCoord()
    return pow(pow(nfc[0]-nft[0], 2)+pow(nfc[1]-nft[1], 2), 0.5)

# ---=========---
#      MAIN
# ---=========---
if __name__ == '__main__':
    # filename = 'SUMO_trafficflow.json'
    # if os.path.exists(filename):
    #     with open (filename,'r+') as ff:
    #         read_data = ff.read()
    #         ff.seek(0)
    #         ff.truncate()
    # else:
    #     ff = open (filename,'x')
    # dt = 0.0167
    # server = SocketServerSimple("127.0.0.1",25001,dt)
    # server.messageToSend = "default"

    # thread1 = threading.Thread(target=server.start)
    # thread2 = threading.Thread(target=TraciServer, args=(server,dt))

    # thread1.start()
    # thread2.start()

    # serverArd = SocketServerSimple("127.0.0.1", 25002,dt)
    # serverArd.messageToSend = "default"

    # thread3 = threading.Thread(target=serverArd.start)
    # thread4 = threading.Thread(target=ArduinoConnection, args=(serverArd,dt))
    # thread3.start()
    # thread4.start()






    # net = sumolib.net.readNet("C:/Users/Napoleon the Beast/Documents/TianZheng/SUMOTest/CircleJunction/Circle.net.xml")
    # newVehicletype = 'private'
    # AdjacencyList = generateTopology()
    # templete = net.getEdges()[0]
    # # print(templete)
    # # print(type(templete))

    # # print(AdjacencyList.keys())
    # # print(AdjacencyList)
    # # addCar()
    # traci.route.add(routeID="newRoute", edges=['1'])

    # net = sumolib.net.readNet("C:/Users/Napoleon the Beast/Documents/TianZheng/SUMOTest/CircleJunction/Circle.net.xml")
    # newVehicletype = 'private'
    # AdjacencyList = generateTopology()
    # templete = net.getEdges()[0]
    # print(templete)
    # print(type(templete))

    # print(AdjacencyList.keys())
    # print(AdjacencyList)
    # addCar()
    


    ## read all vehicles' trajectories
    trajectories = pd.read_csv("C:/Users/Napoleon the Beast/Documents/TianZheng/Esmini/esmini-2.31.9/esmini-2.31.9/sim.csv",sep=",",header=1)
    # print(trajectories)
    # # print(trajectories)
    # print(trajectories.loc[0][' x'])
    # print(trajectories.loc[0][' #1 World_Pitch_Angle [rad] ']/3.14*180)
    # print(trajectories.loc[:][' #1 World_Heading_Angle [rad] ']/3.14*180)

    ## sampling time
    # dt = 0.0167
    dt = 0.05
    offset_x = 233.85 #FourWaySignalL: 117,21; Circle: 233.85
    offset_y = 109.72 #FourWaySignalL: 80.39; Circle: 109.72

    # start sumo
    traci.start(["sumo-gui","-c", "C:/Users/Napoleon the Beast/Documents/TianZheng/Esmini/esmini-2.31.9/esmini-2.31.9/SUMOtest/simulation.sumocfg","--num-clients", "1"])
    traci.setOrder(0)
    step = 0

    

    ## initialization of vehicles using random route
    # random route reader
    pd_reader = pd.read_csv("C:/Users/Napoleon the Beast/Documents/TianZheng/Esmini/esmini-2.31.9/esmini-2.31.9/SUMOtest/result.rou.csv",sep=";")
    randomRoute = pd_reader.loc[0]['route_edges'].split(" ")
    # initialization
    traci.route.add("InitialRoute", randomRoute)
    traci.vehicle.add("Ego_vehicle", "InitialRoute", typeID="EgoBike")

    


    while True:
        traci.simulationStep()
        
        time.sleep(dt)
        # traci.vehicle.moveToXY("Ego_vehicle","", 1 ,102+dt*step,75,0,2)
        # traci.vehicle.moveToXY("Ego_vehicle","", 1 ,trajectories.loc[0][' #1 World_Position_X [m] ']+offset_x,trajectories.loc[0][' #1 World_Position_Y [m] ']+offset_y,-1073741824.0,2)
        traci.vehicle.moveToXY("Ego_vehicle","", 1 ,trajectories.loc[step*4][' x']+offset_x,trajectories.loc[step*4][' y']+offset_y,-1073741824.0,2)
        step += 1


    


    
