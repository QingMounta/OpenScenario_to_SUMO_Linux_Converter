import ctypes
import sys
import pandas as pd
import xml.etree.ElementTree as ET
import os
import logging




Lib_path = "../bin/esminiLib.dll"
esmini_lib = ctypes.CDLL(Lib_path)
print(esmini_lib)

# if (len(sys.argv) < 2):
#     print('Usage: {} <xosc file>'.format(sys.argv[0]))
#     exit(-1)



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

# esmini_lib.SE_Init(sys.argv[1].encode('ascii'), 0, 1, 0, 0)

esmini_lib.SE_Init(b"../resources/myresources/OSC-ALKS-scenarios/Scenarios/ALKS_Scenario_4_4_2_CutInUnavoidableCollision.xosc", 1, 1, 0, 0, 2)

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
        df.loc[Index, f'#{obj_num} collision_ids'] = None



        # print('Index {}, Timestamp {:.4f},  Entitity_Name [-]  {},  Entitity_ID [-]  {},  Current_Speed [m/s]  {:.6f}, '
        #     'Wheel_Angle [deg]  {:.6f}, Wheel_Rotation [-] {:.6f}, '
        #     'bb_x [m] {:.2f}, bb_y [m] {:.2f}, bb_z [m] {:.2f}, '
        #     'bb_width [m] {:.2f}, bb_length [m] {:.2f}, bb_height [m] {:.2f}, '
        #     'World_Position_X [m] {:.6f},World_Position_Y [m] {:.6f},World_Position_Z [m] {:.6f}, '
        #     'Vel_X [m/s] {:.6f}, Vel_Y [m/s] {:.6f}, Vel_Z [m/s] {:.6f}, '
        #     'roadId {} laneId {} laneOffset {:.2f} '
        #     's {:.2f} x {:.6f} y {:.6f} heading {:.2f}  '.format(
        #             Index, obj_state.timestamp, obj_state.objectCategory, obj_state.id, obj_state.speed, 
        #             obj_state.wheelAngle, obj_state.wheelRot, 
        #             obj_state.centerOffsetX, obj_state.centerOffsetY, obj_state.centerOffsetZ, 
        #             obj_state.length, obj_state.width, obj_state.height, 
        #             obj_state.x, obj_state.y, obj_state.z,
        #             obj_state.x, obj_state.y, obj_state.z, 
        #             obj_state.roadId, obj_state.laneId, obj_state.laneOffset,
        #             obj_state.s, obj_state.x, obj_state.y, obj_state.h))
    # esmini_lib.SE_Step()
    esmini_lib.SE_StepDT(DeltaT)
    Index += 1

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
file_path = "../resources/myresources/OSC-ALKS-scenarios/Scenarios/ALKS_Scenario_4_4_2_CutInUnavoidableCollision.xosc"
# file_path = "../resources/myresources/SampleScenarios/575d7e80-10e8-4f39-84b3-ddb52fbf6089.xosc"
# file_path = "../resources/myresources/Circle/circle.xosc"
tree = ET.parse(file_path)
root = tree.getroot()


Entities = tree.find("Entities")
print(list(Entities))
obj_num = 1
for object in Entities:
    Entities_name = object.attrib.get('name')
    print(Entities_name)
    df.loc[:, f'#{obj_num} Entitity_Name [-]'] = Entities_name
    obj_num += 1



# Write DataFrame to Excel file
excel_file_name = 'loggingTrajectories.xlsx'
df.to_excel(excel_file_name, index=False)

# Log the action
with open('log.txt', 'a') as log_file:
    log_file.write(f"DataFrame written to {excel_file_name}\n")    