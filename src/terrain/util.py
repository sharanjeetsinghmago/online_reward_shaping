import numpy as np
import ctypes
from PyQt5.QtGui import QMatrix4x4
def QtoCtype(array):
    arr = np.array(array,dtype=np.float32)
    return arr.ctypes.data_as(np.ctypes.POINTER(np.ctypes.c_float * arr.size))[0]