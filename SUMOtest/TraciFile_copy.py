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
import numpy as np


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
    def __init__(self, id, length, bb_center):
        self.id = id
        self.length = length
        self.bb_center = bb_center
        self.half_length = length / 2
        self.bb_center_ref2frontmid = [self.half_length+bb_center[0],bb_center[1]]
        self.x_front = 0
        self.y_front = 0
        self.t_front = 0
        self.route = []
        self.vehicle_pos_xosc_index = 0
        self.change2sumo = False
        self.changed = False



def find_edge_from_lane(net, lane_id):
    try:
        lane = net.getLane(lane_id)
        edge = lane.getEdge()
        return edge.getID()
    except KeyError:
        # Handle the case when lane ID does not exist in the network
        return ""

def getNearestPos(ID,Vehicle_Num,logging4sumo,vehicle_pos,threshold):
    target_veh = ID
    logging4sumo_this_ID = logging4sumo[logging4sumo["EntityID"] == target_veh]
    min_distance = float('inf')
    min_x, min_y = None, None
    min_index = None

    for index, row in logging4sumo_this_ID.iterrows():
        x, y = row['World_Position_X[m]'], row['World_Position_Y[m]']
        
        # Calculate Euclidean distance between (x, y) and (x_test, y_test)
        distance = math.sqrt((x - vehicle_pos[0]) ** 2 + (y - vehicle_pos[1]) ** 2)
        
        # Update minimum distance and corresponding coordinates and index if applicable
        if distance < min_distance:
            min_distance = distance
            min_x, min_y = x, y
            min_index = index
    # Check if the minimum distance is less than the threshold and return the result
    if min_distance < threshold:
        return min_index
    else:
        return float('inf')
    
def OpenscenarioInfoConvert(filename):
    # Reorganize full_log.csv
    trajectories = pd.read_csv("outputfolder_"+filename+"/full_log.csv",sep=",",header=6)
    Vehicle_Num=int((trajectories.shape[1] - 3) / 31)

    excel_file_path = "outputfolder_"+filename+"/organized_full_log.xlsx"

    # Write the DataFrame to Excel
    trajectories.to_excel(excel_file_path, index=False)
    

    ## sampling time
    dt = 0.025


    #Get Offset and write into infos4unity.txt
    retval = os.getcwd()
    os.chdir( retval+"/outputfolder_"+filename )
    print(os.getcwd())
    net = sumolib.net.readNet("OpenSCENARIO_output.net.xml")
    with open("OpenSCENARIO_output.net.xml", 'r') as file:
        for line in file:
            if 'location netOffset' in line:
                offset_data = line.strip().split('"')[1].split(',')   
    os.chdir( retval )
    
    offset_x = float(offset_data[0]) #FourWaySignalL: 117,21; Circle: 233.85
    offset_y = float(offset_data[1]) #FourWaySignalL: 80.39; Circle: 109.72

    with open("infos4unity.txt", "w") as file:
        # write value of offset_x
        file.write(f"offset_x: {offset_x}\n")
        # write value of offset_y
        file.write(f"offset_y: {offset_y}\n")
    
    
    # ==============================
    # Convert Trajectory (point at the defined middle point of each participant) to Trajectory used in SUMO, store in loggingData4SUMO.xlsx
    # ==============================
    

    # start sumo
    # traci.start(["sumo-gui","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    traci.start(["sumo","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    
    traci.setOrder(0)
    step = 0



    ## initialization of vehicles using random route
    # random route reader
    pd_reader = pd.read_csv("outputfolder_"+filename+"/result.rou.csv",sep=";")
    randomRoute = pd_reader.loc[0]['route_edges'].split(" ")
    # initialization
    traci.route.add("InitialRoute", randomRoute)

    # print(randomRoute)
    for iter in range(1,Vehicle_Num+1):
        Vehicle_ID =  "vehicle" + str(iter) 
        traci.vehicle.add(Vehicle_ID, "InitialRoute", typeID="Car")
        traci.vehicle.setLaneChangeMode(Vehicle_ID, 0)
        
    traci.vehicle.add("Ego", "InitialRoute", typeID="Car")  ## change the bike1 with any other name of your ego participant set in unity

    # Creating a dictionary to store Vehicle objects with their IDs as keys
    vehicles = {}


    # # Create an empty DataFrame with desired columns
    logging4sumo_data = []

    

    while step < trajectories.shape[0]-1:
    # while step < 1:
        traci.simulationStep()
        
        # time.sleep(dt)
        if step == 0:
        # if True:
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                vehicle_length  = trajectories.loc[0][' #' + str(iter) + ' bb_length [m] ']
                bounding_box_center = [trajectories.loc[0][' #' + str(iter) + ' bb_x [m] '],trajectories.loc[0][' #' + str(iter) + ' bb_y [m] ']]
                
                vehicles[Vehicle_ID] = Vehicle(Vehicle_ID, vehicle_length,bounding_box_center)

                print("bb_center reference 2 front mid of ",Vehicle_ID,": ", vehicles[Vehicle_ID].bb_center_ref2frontmid)
                

                x_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
                y_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y


                # print("\n")
                # print("init position of ",Vehicle_ID,": ", x_mid,y_mid)
                traci.vehicle.moveToXY(Vehicle_ID," ", 1 ,x_mid,y_mid,-1000000,2)

            traci.simulationStep()
            # time.sleep(dt)
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 

                # add edge id in route
                lane_id_init = traci.vehicle.getLaneID(Vehicle_ID)
                edge_id_init = find_edge_from_lane(net, lane_id_init)
                vehicles[Vehicle_ID].route.append(edge_id_init)

                # # add lane ID in route
                # lane_id_init = traci.vehicle.getLaneID(Vehicle_ID)
                # vehicles[Vehicle_ID].route.append(lane_id_init)


            traci.simulationStep()
            # time.sleep(dt)
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 

                


                angle_init_degree = traci.vehicle.getAngle(Vehicle_ID)
                print("angle: ",angle_init_degree)
                x_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
                y_mid = trajectories.loc[0][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y

                vehicles[Vehicle_ID].x_front = x_mid+math.sin(np.deg2rad(angle_init_degree))*vehicles[Vehicle_ID].bb_center_ref2frontmid[0]
                vehicles[Vehicle_ID].y_front = y_mid+math.cos(np.deg2rad(angle_init_degree))*vehicles[Vehicle_ID].bb_center_ref2frontmid[0]

                traci.vehicle.moveToXY(Vehicle_ID," ", 1 ,vehicles[Vehicle_ID].x_front,vehicles[Vehicle_ID].y_front,angle_init_degree,2)
                # print("head position of ",Vehicle_ID," at: ", vehicles[Vehicle_ID].x_front,vehicles[Vehicle_ID].y_front)
                
                # Record the time vehicles need to reach their front
                # vehicles[Vehicle_ID].t_front = time_reachFront(trajectories.loc[:][' #' + str(iter) + ' World_Position_X [m] '],trajectories.loc[:][' #' + str(iter) + ' World_Position_Y [m] '],vehicles[Vehicle_ID].bb_center_ref2frontmid[0])
                # print("the steps needed to move from middle to front is ",vehicles[Vehicle_ID].t_front)
                logging4sumo_data.append({"timestamp":trajectories.loc[0][' TimeStamp [s] '],
                                          "EntityName":trajectories.loc[0][' #' + str(iter) + ' Entitity_Name [-] '],
                                          "EntityID":trajectories.loc[0][' #' + str(iter) + ' Entitity_ID [-] '],
                                          "World_Position_X[m]":vehicles[Vehicle_ID].x_front,
                                          "World_Position_Y[m]":vehicles[Vehicle_ID].y_front,
                                          "World_Rotation_Z[m]":angle_init_degree})
    
                # Append the data to the DataFrame
                # logging4sumo = logging4sumo.append(data, ignore_index=True)

        else:
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 

                # add edge id in route    
                lane_id_now= traci.vehicle.getLaneID(Vehicle_ID)
                edge_id_now = find_edge_from_lane(net, lane_id_now)
                if edge_id_now != vehicles[Vehicle_ID].route[-1] and edge_id_now != "":
                    vehicles[Vehicle_ID].route.append(edge_id_now)

                # # add lane id in route    
                # lane_id_now= traci.vehicle.getLaneID(Vehicle_ID)
                # if lane_id_now != vehicles[Vehicle_ID].route[-1] and lane_id_now != "":
                #     vehicles[Vehicle_ID].route.append(lane_id_now)
                
                


                x_mid = trajectories.loc[step][' #' + str(iter) + ' World_Position_X [m] ']+offset_x
                y_mid = trajectories.loc[step][' #' + str(iter) + ' World_Position_Y [m] ']+offset_y
                x_vel = trajectories.loc[step][' #' + str(iter) + ' Vel_X [m/s] ']
                y_vel = trajectories.loc[step][' #' + str(iter) + ' Vel_Y [m/s] ']

                angle_vehicle_radian = math.atan2(x_vel, y_vel)
                angle_vehicle_degrees = math.degrees(angle_vehicle_radian)


                
                vehicles[Vehicle_ID].x_front = x_mid + vehicles[Vehicle_ID].bb_center_ref2frontmid[0]*math.sin(angle_vehicle_radian)
                vehicles[Vehicle_ID].y_front = y_mid + vehicles[Vehicle_ID].bb_center_ref2frontmid[0]*math.cos(angle_vehicle_radian)
                
                traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,vehicles[Vehicle_ID].x_front,vehicles[Vehicle_ID].y_front,angle_vehicle_degrees,2)

                logging4sumo_data.append({"timestamp":trajectories.loc[step][' TimeStamp [s] '],
                                          "EntityName":trajectories.loc[step][' #' + str(iter) + ' Entitity_Name [-] '],
                                          "EntityID":trajectories.loc[step][' #' + str(iter) + ' Entitity_ID [-] '],
                                          "World_Position_X[m]":vehicles[Vehicle_ID].x_front,
                                          "World_Position_Y[m]":vehicles[Vehicle_ID].y_front,
                                          "World_Rotation_Z[m]":angle_vehicle_degrees})
    
                # Append the data to the DataFrame
                # logging4sumo = logging4sumo.append(data, ignore_index=True)


        # time.sleep(dt)
        step += 1

    for iter in range(1,Vehicle_Num+1):
        Vehicle_ID =  "vehicle" + str(iter) 
        print(vehicles[Vehicle_ID].route)

        
    traci.close()


    logging4sumo = pd.DataFrame(logging4sumo_data)
    excel_file = "outputfolder_"+filename+"/loggingData4SUMO.xlsx"
    logging4sumo.to_excel(excel_file, index=False)


    return Vehicle_Num, vehicles, logging4sumo, net


def TraciSUMOServer(server,dt,filename,Vehicle_Num, vehicles, logging4sumo, net):
    # start sumo
    traci.start(["sumo-gui","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    # traci.start(["sumo","-c", "outputfolder_"+filename+"/simulation.sumocfg","--num-clients", "1"])
    
    traci.setOrder(0)
    step = 0
    allChange2SUMO = False
    changed = False

    for iter in range(1,Vehicle_Num+1):
        Vehicle_ID =  "vehicle" + str(iter)
        Route_ID = "InitialRoute" + str(iter)
        traci.route.add(Route_ID, vehicles[Vehicle_ID].route)
        traci.vehicle.add(Vehicle_ID, Route_ID, typeID="Car")
        traci.vehicle.setLaneChangeMode(Vehicle_ID, 0)
    traci.vehicle.add("Ego", "InitialRoute1", typeID="Car")
    
    # net = sumolib.net.readNet("outputfolder_"+filename+"/"+filename+".net.xml")

    # while step < trajectories.shape[0]-1:
    for _ in range(int(10/dt)):
        traci.simulationStep()
        time.sleep(dt)
    while step < 50/dt:
        traci.simulationStep()
        
        time.sleep(dt)
        

        

        # ==============================
        # Send Values from Unity to SUMO (Detect distance between surronding vehicles and ego)
        # ==============================
        # Ego Vehicle
        try:

            msg = json.loads(server.messageReceived)
            traci.vehicle.moveToXY("Ego","", 1 ,msg["positionX"],msg["positionY"],msg["rotation"],2)
            distance = []
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                pos_surrounding_veh = traci.vehicle.getPosition(Vehicle_ID)
                distance.append(math.sqrt((pos_surrounding_veh[0] - msg["positionX"]) ** 2 + (pos_surrounding_veh[1] - msg["positionY"]) ** 2))

            if all(item >= 5 for item in distance):
                allChange2SUMO = False
            else:
                allChange2SUMO = True
            #traci.vehicle.setSpeed(msg["id"],msg["speed"])

            
        except:
            pass




        # ==============================
        # Preparation for Values from SUMO to Unity (Detect obstacles to change between trajectory control and SUMO control)
        # ==============================
        
        # Situation 1: Trajectory control: Not enconter any obstacles or change back from SUMO control
        if  allChange2SUMO == False and changed == False:
            
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                
                # Situation 1.1: Not pass through the whole trajectory yet, while not encounter any obstacles
                if Vehicle_Num*step+iter-1 < logging4sumo.shape[0] and vehicles[Vehicle_ID].vehicle_pos_xosc_index == 0:
                    x_sumo = logging4sumo.loc[Vehicle_Num*step+iter-1]['World_Position_X[m]']
                    y_sumo = logging4sumo.loc[Vehicle_Num*step+iter-1]['World_Position_Y[m]']
                    angle_sumo = logging4sumo.loc[Vehicle_Num*step+iter-1]['World_Rotation_Z[m]']
                    traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,x_sumo,y_sumo,angle_sumo,2)  

                # Situation 1.2: Encounter >= 1 time the obstacle, and the position of surronding vehicles stay still inside the defined trajectory
                elif 0 < vehicles[Vehicle_ID].vehicle_pos_xosc_index < logging4sumo.shape[0]:
                    vehicles[Vehicle_ID].vehicle_pos_xosc_index += Vehicle_Num

                    if vehicles[Vehicle_ID].vehicle_pos_xosc_index < logging4sumo.shape[0]:
                        x_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Position_X[m]']
                        y_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Position_Y[m]']
                        angle_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Rotation_Z[m]']
                        # print(Vehicle_ID,x_sumo,y_sumo,angle_sumo)


                        traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,x_sumo,y_sumo,angle_sumo,2)
                    else:
                        break
                else:
                    break

        # Situation 2: SUMO control: change from Trajectory control to SUMO control
        elif allChange2SUMO == True and changed == False:

            changed = True
            print("now changed to SUMO control, variable allchange2sumo is: ",allChange2SUMO,"changed is: ",changed) 
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                
                vehicle_pos_now = traci.vehicle.getPosition(Vehicle_ID)
                lane = net.getNeighboringLanes(vehicle_pos_now[0], vehicle_pos_now[1], includeJunctions=False)[0][0]
                pos_lane = lane.getClosestLanePosAndDist((vehicle_pos_now[0], vehicle_pos_now[1]))[0]

                traci.vehicle.moveTo(Vehicle_ID, lane.getID(), pos_lane)  # not working on internal lanes
        
        # Situation 3: Trajectory control: change back to trajectory control and check the most nearest transit point on the trajectory
        elif allChange2SUMO == False and changed == True:
            print("now change back to Trajectory following control, system is finding the nearest point on the trajectory for each participants, variable allchange2sumo is: ",allChange2SUMO,"changed is: ",changed) 
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                
                vehicle_pos = traci.vehicle.getPosition(Vehicle_ID)
                threshold = 1
                vehicle_pos_xosc_index = getNearestPos(iter-1,Vehicle_Num,logging4sumo,vehicle_pos,threshold)
                vehicles[Vehicle_ID].vehicle_pos_xosc_index = vehicle_pos_xosc_index
                print(Vehicle_ID,"now at xosc pos with index ",vehicle_pos_xosc_index)
                if vehicle_pos_xosc_index != float('inf'):
                    x_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Position_X[m]']
                    y_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Position_Y[m]']
                    angle_sumo = logging4sumo.loc[vehicles[Vehicle_ID].vehicle_pos_xosc_index]['World_Rotation_Z[m]']
                    traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,x_sumo,y_sumo,angle_sumo,2)
                else:
                    print(Vehicle_ID," could not go back to predesigned trajectory.")
                    break
            changed = False 

        # Situation 4: 
        elif allChange2SUMO == False:
            for iter in range(1,Vehicle_Num+1):
                Vehicle_ID =  "vehicle" + str(iter) 
                # if vehicles[Vehicle_ID].vehicle_pos_xosc_index == 0 and Vehicle_Num*step+iter-1 >= logging4sumo.shape[0]:
                vehicle_pos_final = traci.vehicle.getPosition(Vehicle_ID)
                angle_final_degree = traci.vehicle.getAngle(Vehicle_ID)
                traci.vehicle.moveToXY(Vehicle_ID,"", 1 ,vehicle_pos_final[0],vehicle_pos_final[1],angle_final_degree,2)
        


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


        sumoSimStep = SumoSimulationStepInfo(simulationTime,vehicleList,0).__dict__
        server.messageToSend = json.dumps(sumoSimStep)

        
        
        step += 1

    

        
    traci.close()

    
# ---=========---
#      MAIN
# ---=========---
if __name__ == '__main__':




    if len(sys.argv) < 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)


    filename = sys.argv[1]

    # ==============================
    # Convert Trajectory used in Openscenario to Trajectory used in SUMO, store in loggingData4SUMO.xlsx
    #
    # Vehicle_Num: Number of participants in the Openscenario scneario
    # vehicles: Dictionary, store all the infos of each participants defined in the Openscenario scneario
    # logging4sumo: Trajectory data suilt for SUMO
    # net: Converted net from Opendrive map  
    # ==============================
    Vehicle_Num, vehicles, logging4sumo, net = OpenscenarioInfoConvert(filename)



    ## sampling time
    dt = 0.025

    server = SocketServerSimple("127.0.0.1",25001,dt)
    server.messageToSend = "default"

    thread1 = threading.Thread(target=server.start)

    # ==============================
    # Control the participants in the scenario by trajectory control or SUMO control depends on the distance between the participants and obstacles controled in unity. 
    # ==============================
    thread2 = threading.Thread(target=TraciSUMOServer, args=(server,dt,filename,Vehicle_Num, vehicles, logging4sumo, net))

    thread1.start()
    thread2.start()



    serverArd = SocketServerSimple("127.0.0.1", 25002,dt)
    serverArd.messageToSend = "default"

    thread3 = threading.Thread(target=serverArd.start)
    thread4 = threading.Thread(target=ArduinoConnection, args=(serverArd,dt))
    thread3.start()
    thread4.start()



    

    




