from simulator3d import GLWidget
from rewardtraining import InitTrain
import sys
import math

from PyQt5.QtCore import Qt, pyqtSlot, QTime
from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4, QPainter, QColor, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget


    
class Simulator():
    def __init__(self, parent):
        self.widget = GLWidget(None)
        self.widget.resize(640, 480)
        self.widget.show()
        self.widget.maskCreated.connect(self.sendMask)
        self.learningModel = InitTrain()
        self.learningModel.inititaltrain()
    def sendMask(self, mask):
        self.learningModel.phasetrain(mask, 1)
        print(mask)

    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    simul = Simulator(None)

    sys.exit(app.exec_())