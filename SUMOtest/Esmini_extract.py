import ctypes
import sys

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

esmini_lib.SE_Init(b"../resources/xosc/cut-in.xosc", 1, 1, 0, 0, 2)



# esmini_lib.SE_Init(sys.argv[1].encode('ascii'), 0, 1, 0, 0)
obj_state = SEScenarioObjectState()  # object that will be passed and filled in with object state info

esmini_lib.SE_StepDT.argtypes = [ctypes.c_float]

for i in range(500):
    for j in range(esmini_lib.SE_GetNumberOfObjects()):
        esmini_lib.SE_GetObjectState(esmini_lib.SE_GetId(j), ctypes.byref(obj_state))
        print('Frame {} Time {:.4f} ObjId {} roadId {} laneId {} laneOffset {:.2f} s {:.2f} x {:.2f} y {:.2f} heading {:.2f} speed {:.2f} wheelAngle {:.2f} wheelRot {:.2f}'.format(
            i, obj_state.timestamp, obj_state.id, obj_state.roadId, obj_state.laneId, obj_state.laneOffset,
            obj_state.s, obj_state.x, obj_state.y, obj_state.h, obj_state.speed * 3.6, obj_state.wheelAngle, obj_state.wheelRot))
    # esmini_lib.SE_Step()
    esmini_lib.SE_StepDT(0.02)