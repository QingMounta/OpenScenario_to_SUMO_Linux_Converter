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
import math
import sys
import openpyxl


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



class Vehicle:
    def __init__(self, id, length):
        self.id = id
        self.length = length
        self.half_length = length / 2
        self.x_front = None
        self.y_front = None
        self.t_front = None
        self.route = []

def is_position_inside(x, y, polygon,print_flag):
    crossings = False
    n = len(polygon)

    for i in range(n-1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1)]

        if y2!=y1:
            margin = abs(0.3/(y2 - y1))
        else:
            margin = 0

        if ((y1 <= y < y2) or (y2 <= y < y1)) and ((x2 - x1) * (y - y1) / (y2 - y1) + x1 - margin < x < (x2 - x1) * (y - y1) / (y2 - y1) + x1 + margin):
            crossings = True
            if print_flag == True:
                print("\n")
                print((x2 - x1) * (y - y1) / (y2 - y1) + x1 - margin,x,(x2 - x1) * (y - y1) / (y2 - y1) + x1 + margin)
                print("\n")
                print(x1,x,x2)
                print("\n")
                print(y1,y,y2)
                

    return crossings

def angle_inlane(x, y, polygon):
    crossings = 0
    n = len(polygon)

    for i in range(n-1):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1)]
        if y2!=y1:
            margin = abs(0.3/(y2 - y1))
        else:
            margin = 0
        if ((y1 <= y < y2) or (y2 <= y < y1)) and ((x2 - x1) * (y - y1) / (y2 - y1) + x1 - margin < x < (x2 - x1) * (y - y1) / (y2 - y1) + x1+margin):
            angle = math.atan2(x2 - x1, y2 - y1)
            angle_degrees = math.degrees(angle)
    return angle

def time_reachFront(x_pos_list,y_pos_list,half_vehicle_length):
    
    x0 = x_pos_list[0]
    y0 = y_pos_list[0]
    i = 0

    dist_from_begin = 0
    while dist_from_begin < half_vehicle_length:
        i += 1
        dist_from_begin = math.sqrt((x_pos_list[i] - x0)**2 + (y_pos_list[i] - y0)**2)
  
    time_front = i
    return time_front

def find_edge_from_lane(net, lane_id):
    try:
        lane = net.getLane(lane_id)
        edge = lane.getEdge()
        return edge.getID()
    except KeyError:
        # Handle the case when lane ID does not exist in the network
        return ""


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




    if len(sys.argv) < 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)


    filename = sys.argv[1]


    

    # from full_log.csv
    # static_trajectories = pd.read_csv("outputfolder_"+filename+"/sim.csv",sep=",",header=1)

    trajectories = pd.read_csv("outputfolder_"+filename+"/full_log.csv",sep=",",header=6)
    Vehicle_Num=int((trajectories.shape[1] - 3) / 31)

    excel_file_path = "outputfolder_"+filename+"/organized_full_log.xlsx"

    # Write the DataFrame to Excel
    trajectories.to_excel(excel_file_path, index=False)

    
    



    ## sampling time
    dt = 0.025

    #Get offset
    net = sumolib.net.readNet("outputfolder_"+filename+"/"+filename+".net.xml")
    with open("outputfolder_"+filename+"/"+filename+".net.xml", 'r') as file:
        for line in file:
            if 'location netOffset' in line:
                offset_data = line.strip().split('"')[1].split(',')   
    offset_x = float(offset_data[0]) #FourWaySignalL: 117,21; Circle: 233.85
    offset_y = float(offset_data[1]) #FourWaySignalL: 80.39; Circle: 109.72
    print(offset_x,offset_y)
    

    # start sumo
    traci.start(["sumo-gui","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    # traci.start(["sumo","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    
    traci.setOrder(0)
    step = 0
    

    # ## initialization of vehicles using random route
    # # random route reader
    # pd_reader = pd.read_csv("outputfolder_"+filename+"/result.rou.csv",sep=";")
    # randomRoute = pd_reader.loc[0]['route_edges'].split(" ")
    # # initialization
    # traci.route.add("InitialRoute", randomRoute)
    # for iter in range(1,Vehicle_Num+1):
    #     Vehicle_ID =  "vehicle" + str(iter) 
    #     traci.vehicle.add(Vehicle_ID, "InitialRoute", typeID="Car")


    # Creating a dictionary to store Vehicle objects with their IDs as keys
    vehicles = {}


    lane_ids = traci.lane.getIDList()
            
    for lane_id in lane_ids:
        
        lane_shape = traci.lane.getShape(lane_id)
        print(lane_id,lane_shape)
    
    while step < trajectories.shape[0]:
        for iter in range(1,Vehicle_Num+1):
            Vehicle_ID =  "vehicle" + str(iter)

            if step == 0:
                vehicle_length  = trajectories.loc[0][' #' + str(iter) + ' bb_length [m] ']
                vehicles[Vehicle_ID] = Vehicle(Vehicle_ID, vehicle_length)

            x_mid = trajectories.loc[step][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
            y_mid = trajectories.loc[step][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y
            lane_ids = traci.lane.getIDList()
            
            for lane_id in lane_ids:
                
                lane_shape = traci.lane.getShape(lane_id)
                # Check if the position (x, y) is within the lane's shape
                if is_position_inside(x_mid, y_mid, lane_shape,True):
                    
                    edge_id = find_edge_from_lane(net, lane_id)
                    if vehicles[Vehicle_ID].route != []:
                        if edge_id != vehicles[Vehicle_ID].route[-1] and edge_id != "":
                            vehicles[Vehicle_ID].route.append(edge_id)
                    else:
                        vehicles[Vehicle_ID].route.append(edge_id)
                    # vehicles[Vehicle_ID].route.append(lane_id)

                    

        
        step += 1

    txt_filename = "route_list.txt"
    with open(txt_filename, 'w') as file:
        file.write('')
    # route_df = pd.DataFrame()
    for iter in range(1,2):
        Vehicle_ID =  "vehicle" + str(iter)
        
        # Write the list to the text file
        with open(txt_filename, "a") as file:
            file.write(Vehicle_ID + ": ")
            for item in vehicles[Vehicle_ID].route:
                file.write(item)
            file.write("\n")
            file.write("\n")
        print(vehicles[Vehicle_ID].route)



        # # traci.vehicle.setRoute(Vehicle_ID, vehicles[Vehicle_ID].route)

        # traci.route.add("InitialRoute1", vehicles[Vehicle_ID].route)
        # traci.vehicle.add(Vehicle_ID, "InitialRoute1", typeID="Car")
        # x_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
        # y_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y
        # traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,x_mid,y_mid,-10000000,2)

        # # traci.vehicle.moveTo(Vehicle_ID, vehicles[Vehicle_ID].route[0], pos=50)



    

    for _ in range(50000):
            traci.simulationStep()












    # step = 0
    # while step < trajectories.shape[0]:
    # # while step < 10:
    #     traci.simulationStep()
        
    #     time.sleep(dt)
    #     if step == 0:
    #     # if True:
    #         for iter in range(1,Vehicle_Num+1):
    #             Vehicle_ID =  "vehicle" + str(iter) 
    #             vehicle_length  = trajectories.loc[0][' #' + str(iter) + ' bb_length [m] ']
    #             vehicles[Vehicle_ID] = Vehicle(Vehicle_ID, vehicle_length)

    #             half_vehicle_length = vehicles[Vehicle_ID].length/2
                

    #             x_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
    #             y_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y



    #             lane_ids = traci.lane.getIDList()
    #             for lane_id in lane_ids:
    #                 lane_shape = traci.lane.getShape(lane_id)
    #                 # Check if the position (x, y) is within the lane's shape
    #                 if is_position_inside(x_mid, y_mid, lane_shape):

    #                     angle_lane_radian = angle_inlane(x_mid, y_mid, lane_shape)
    #                     angle_lane_degrees = math.degrees(angle_lane_radian)

                
    #             vehicles[Vehicle_ID].x_front = x_mid+math.sin(angle_lane_radian)*half_vehicle_length
    #             vehicles[Vehicle_ID].y_front = y_mid+math.cos(angle_lane_radian)*half_vehicle_length
    #             traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,vehicles[Vehicle_ID].x_front,vehicles[Vehicle_ID].y_front,angle_lane_degrees,2)

    #             # Record the time vehicles need to reach their front
    #             vehicles[Vehicle_ID].t_front = time_reachFront(trajectories.loc[:][' #' + str(iter) + ' World_Position_X [m] '],trajectories.loc[:][' #' + str(iter) + ' World_Position_Y [m] '],half_vehicle_length)

    #     else:
    #         for iter in range(1,Vehicle_Num+1):
    #             Vehicle_ID =  "vehicle" + str(iter) 
                
    #             if step+vehicles[Vehicle_ID].t_front < trajectories.shape[0]:
    #                 x_vel = trajectories.loc[step+vehicles[Vehicle_ID].t_front][' #' + str(iter) + ' Vel_X [m/s] ']
    #                 y_vel = trajectories.loc[step+vehicles[Vehicle_ID].t_front][' #' + str(iter) + ' Vel_Y [m/s] ']
    #             else:
    #                 x_vel = 0
    #                 y_vel = 0
                    
                
    #             angle_vehicle_radian = math.atan2(x_vel, y_vel)
    #             angle_vehicle_degrees = math.degrees(angle_vehicle_radian)

                
    #             vehicles[Vehicle_ID].x_front = vehicles[Vehicle_ID].x_front + x_vel * dt
    #             vehicles[Vehicle_ID].y_front = vehicles[Vehicle_ID].y_front + y_vel * dt
                
    #             traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,vehicles[Vehicle_ID].x_front,vehicles[Vehicle_ID].y_front,angle_vehicle_degrees,2)


        
    #     step += 1



        
    traci.close()

    


    


    
