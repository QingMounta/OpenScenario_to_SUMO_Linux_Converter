import ctypes
import sys
import pandas as pd
import xml.etree.ElementTree as ET
import os
import logging
import re
import imageio
import shutil

import Esmini_get

if len(sys.argv) < 3:
        print("Usage: python Esmini_extract.py <filename> <folderpath>")
        sys.exit(1)


filename = sys.argv[1]
folderpath = sys.argv[2]

Bin_Path = Esmini_get.download_Esmini_getBinPath()
Lib_path = Bin_Path+"/esminiLib.dll"
esmini_lib = ctypes.CDLL(Lib_path)
print(esmini_lib)



# Definition of SE_ScenarioObjectState struct
class SEScenarioObjectState(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("model_id", ctypes.c_int),
        ("control", ctypes.c_int),
        ("timestamp", ctypes.c_float),
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("h", ctypes.c_float),
        ("p", ctypes.c_float),
        ("r", ctypes.c_float),
        ("roadId", ctypes.c_int),
        ("junctionId", ctypes.c_int),
        ("t", ctypes.c_float),
        ("laneId", ctypes.c_int),
        ("laneOffset", ctypes.c_float),
        ("s", ctypes.c_float),
        ("speed", ctypes.c_float),
        ("centerOffsetX", ctypes.c_float),
        ("centerOffsetY", ctypes.c_float),
        ("centerOffsetZ", ctypes.c_float),
        ("width", ctypes.c_float),
        ("length", ctypes.c_float),
        ("height", ctypes.c_float),
        ("objectType", ctypes.c_int),
        ("objectCategory", ctypes.c_int),
        ("wheelAngle", ctypes.c_float),
        ("wheelRot", ctypes.c_float),
    ]



file_path = "../"+folderpath+"/"+filename+".xosc"
# file_path = "../EnvironmentSimulator/Unittest/xosc/test-collision-detection.xosc"

class WindowSize:
        """
        Utility class storing information about the size and position of a window
        """

        x: int = 0
        y: int = 0
        width: int = 1280
        height: int = 960

esmini_lib.SE_SetWindowPosAndSize(WindowSize.x, WindowSize.y, WindowSize.width, WindowSize.height)

esmini_lib.SE_Init(file_path.encode("ASCII"), 0, 0, 0, 0)


# Assuming NumberOfObjects has a certain value
NumberOfObjects = esmini_lib.SE_GetNumberOfObjects()

# Create columns for Index and TimeStamp
columns = ['Index [-]', 'TimeStamp [s]']

# Create columns for each object based on NumberOfObjects
for obj_num in range(1, NumberOfObjects + 1):
    columns.extend([
        f'#{obj_num} Entitity_Name [-]',
        f'#{obj_num} Entitity_ID [-]',
        f'#{obj_num} Current_Speed [m/s]',
        f'#{obj_num} Wheel_Angle [deg]',
        f'#{obj_num} Wheel_Rotation [-]',
        f'#{obj_num} bb_x [m]',
        f'#{obj_num} bb_y [m]',
        f'#{obj_num} bb_z [m]',
        f'#{obj_num} bb_length [m]',
        f'#{obj_num} bb_width [m]',
        f'#{obj_num} bb_height [m]',
        f'#{obj_num} World_Position_X [m]',
        f'#{obj_num} World_Position_Y [m]',
        f'#{obj_num} World_Position_Z [m]',
        f'#{obj_num} Vel_X [m/s]',
        f'#{obj_num} Vel_Y [m/s]',
        f'#{obj_num} Vel_Z [m/s]',
        f'#{obj_num} Acc_X [m/s2]',
        f'#{obj_num} Acc_Y [m/s2]',
        f'#{obj_num} Acc_Z [m/s2]',
        f'#{obj_num} Distance_Travelled_Along_Road_Segment [m]',
        f'#{obj_num} Lateral_Distance_Lanem [m]',
        f'#{obj_num} lane_id',
        f'#{obj_num} lane_offset [m]',
        f'#{obj_num} World_Heading_Angle [rad]',
        f'#{obj_num} Heading_Angle_Rate [rad/s]',
        f'#{obj_num} Relative_Heading_Angle [rad]',
        f'#{obj_num} Relative_Heading_Angle_Drive_Direction [rad]',
        f'#{obj_num} World_Pitch_Angle [rad]',
        f'#{obj_num} Road_Curvature [1/m]',
        f'#{obj_num} collision_ids'
    ])

# Create an empty DataFrame with the generated columns
df = pd.DataFrame(columns=columns)




    






# esmini_lib.SE_Init(sys.argv[1].encode('ascii'), 0, 1, 0, 0)
obj_state = SEScenarioObjectState()  # object that will be passed and filled in with object state info

esmini_lib.SE_StepDT.argtypes = [ctypes.c_float]
DeltaT = 0.025
Index = 0
esmini_lib.SE_CollisionDetection(True)


while esmini_lib.SE_GetQuitFlag() != 1:
    # Get the number of rows in the DataFrame
    # num_rows = len(df)
    # Write "0" in the last row of the "Index [-]" column
    df.loc[Index, 'Index [-]'] = Index
    df.loc[Index, 'TimeStamp [s]'] = Index * DeltaT
    for obj_num in range(1,esmini_lib.SE_GetNumberOfObjects()+1):
        esmini_lib.SE_GetObjectState(esmini_lib.SE_GetId(obj_num-1), ctypes.byref(obj_state))
        
        df.loc[Index, f'#{obj_num} Entitity_ID [-]'] = obj_state.id
        df.loc[Index, f'#{obj_num} Current_Speed [m/s]'] = obj_state.speed
        df.loc[Index, f'#{obj_num} Wheel_Angle [deg]'] = obj_state.wheelAngle
        df.loc[Index, f'#{obj_num} Wheel_Rotation [-]'] = obj_state.wheelRot
        df.loc[Index, f'#{obj_num} bb_x [m]'] = obj_state.centerOffsetX
        df.loc[Index, f'#{obj_num} bb_y [m]'] = obj_state.centerOffsetY
        df.loc[Index, f'#{obj_num} bb_z [m]'] = obj_state.centerOffsetZ
        df.loc[Index, f'#{obj_num} bb_length [m]'] = obj_state.length
        df.loc[Index, f'#{obj_num} bb_width [m]'] = obj_state.width
        df.loc[Index, f'#{obj_num} bb_height [m]'] = obj_state.height
        df.loc[Index, f'#{obj_num} World_Position_X [m]'] = obj_state.x
        df.loc[Index, f'#{obj_num} World_Position_Y [m]'] = obj_state.y
        df.loc[Index, f'#{obj_num} World_Position_Z [m]'] = obj_state.z

        if Index>0:
            df.loc[Index-1, f'#{obj_num} Vel_X [m/s]'] = (obj_state.x - df.loc[Index-1, f'#{obj_num} World_Position_X [m]'])/DeltaT
            df.loc[Index-1, f'#{obj_num} Vel_Y [m/s]'] = (obj_state.y - df.loc[Index-1, f'#{obj_num} World_Position_Y [m]'])/DeltaT
            df.loc[Index-1, f'#{obj_num} Vel_Z [m/s]'] = (obj_state.z - df.loc[Index-1, f'#{obj_num} World_Position_Z [m]'])/DeltaT

            df.loc[Index-1, f'#{obj_num} Heading_Angle_Rate [rad/s]'] =(obj_state.h - df.loc[Index-1, f'#{obj_num} World_Heading_Angle [rad]'])/DeltaT

        if Index>1:
            df.loc[Index-2, f'#{obj_num} Acc_X [m/s2]'] = (df.loc[Index-1, f'#{obj_num} Vel_X [m/s]'] - df.loc[Index-2, f'#{obj_num} Vel_X [m/s]'])/DeltaT
            df.loc[Index-2, f'#{obj_num} Acc_Y [m/s2]'] = (df.loc[Index-1, f'#{obj_num} Vel_Y [m/s]'] - df.loc[Index-2, f'#{obj_num} Vel_Y [m/s]'])/DeltaT
            df.loc[Index-2, f'#{obj_num} Acc_Z [m/s2]'] = (df.loc[Index-1, f'#{obj_num} Vel_Z [m/s]'] - df.loc[Index-2, f'#{obj_num} Vel_Z [m/s]'])/DeltaT

        df.loc[Index, f'#{obj_num} Distance_Travelled_Along_Road_Segment [m]'] = obj_state.s
        df.loc[Index, f'#{obj_num} Lateral_Distance_Lanem [m]'] = obj_state.t
        df.loc[Index, f'#{obj_num} lane_id'] = obj_state.laneId
        df.loc[Index, f'#{obj_num} lane_offset [m]'] = obj_state.laneOffset
        df.loc[Index, f'#{obj_num} World_Heading_Angle [rad]'] = obj_state.h
        
        df.loc[Index, f'#{obj_num} Relative_Heading_Angle [rad]'] = None
        df.loc[Index, f'#{obj_num} Relative_Heading_Angle_Drive_Direction [rad]'] = None
        df.loc[Index, f'#{obj_num} World_Pitch_Angle [rad]'] = obj_state.p
        df.loc[Index, f'#{obj_num} Road_Curvature [1/m]'] = None

        if esmini_lib.SE_GetObjectNumberOfCollisions(obj_num-1) > 0:
            
            temp_list = []
            for k in range(esmini_lib.SE_GetObjectNumberOfCollisions(obj_num-1)):
                temp_list.append(esmini_lib.SE_GetObjectCollision(obj_num-1, k)+1)
                df.loc[Index, f'#{obj_num} collision_ids'] = temp_list
            print("collision ids now at vehicle: ",obj_num," include ",temp_list)
        else:
            df.loc[Index, f'#{obj_num} collision_ids'] = None
 
    esmini_lib.SE_StepDT(DeltaT)
    Index += 1
esmini_lib.SE_Close()

for obj_num in range(1,esmini_lib.SE_GetNumberOfObjects()+1):
    df.loc[Index-1, f'#{obj_num} Vel_X [m/s]'] = 0
    df.loc[Index-1, f'#{obj_num} Vel_Y [m/s]'] = 0
    df.loc[Index-1, f'#{obj_num} Vel_Z [m/s]'] = 0

    df.loc[Index-1, f'#{obj_num} Heading_Angle_Rate [rad/s]'] = 0

    df.loc[Index-2, f'#{obj_num} Acc_X [m/s2]'] = 0
    df.loc[Index-2, f'#{obj_num} Acc_Y [m/s2]'] = 0
    df.loc[Index-2, f'#{obj_num} Acc_Z [m/s2]'] = 0
    df.loc[Index-1, f'#{obj_num} Acc_X [m/s2]'] = 0
    df.loc[Index-1, f'#{obj_num} Acc_Y [m/s2]'] = 0
    df.loc[Index-1, f'#{obj_num} Acc_Z [m/s2]'] = 0


    




# ==============================
# Get the entity name from xosc file
# ==============================

# Load the OpenSCENARIO file

tree = ET.parse(file_path)
root = tree.getroot()


Entities = tree.find("Entities")
obj_num = 1
for object in Entities:
    Entities_name = object.attrib.get('name')
    df.loc[:, f'#{obj_num} Entitity_Name [-]'] = Entities_name
    obj_num += 1



# Write DataFrame to Excel file
excel_file_name = "outputfolder_"+filename+"/loggingTrajectoriesXOSC.xlsx"
df.to_excel(excel_file_name, index=False)

# Log the action
with open('log.txt', 'a') as log_file:
    log_file.write(f"DataFrame written to {excel_file_name}\n")    



# ==============================
# Get the gif generated while simulation
# ==============================

image_regex = re.compile(r"screen_shot_\d{5,}\.tga")

ignored_images = set(
    [p for p in os.listdir(".") if image_regex.match(p) is not None]
)

for ignored_image in ignored_images:
    os.remove(ignored_image)

esmini_lib.SE_Init(file_path.encode("ASCII"), 0, 7, 0, 0)
esmini_lib.SE_StepDT.argtypes = [ctypes.c_float]
while esmini_lib.SE_GetQuitFlag() != 1:
    esmini_lib.SE_StepDT(DeltaT)
esmini_lib.SE_Close()
images = sorted(
    [
        p
        for p in os.listdir(".")
        if image_regex.match(p) is not None
    ]
)

print("Generating animation of this sceanrio...")
gif_file_path = "outputfolder_"+filename+"/simulation_animation.gif"
with imageio.get_writer(gif_file_path, mode="I", duration=DeltaT*1000) as writer:
    for image in images:
        writer.append_data(imageio.v3.imread(image))
        os.remove(image)
print("Animation generated in folder ","outputfolder_"+filename)
# Log the action
with open('log.txt', 'a') as log_file:
    log_file.write(f"Animation generated in {gif_file_path}\n")    

# shutil.move('log.txt', "outputfolder_"+filename+"/log.txt")