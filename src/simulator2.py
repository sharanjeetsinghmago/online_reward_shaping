from simulator3d import GLWidget
from rewardtraining import InitTrain
import sys
import math

from PyQt5.QtCore import Qt, pyqtSlot, QTime
from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4, QPainter, QColor, QPen
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget

import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt



def discrete_matshow(data, filename, vmin, vmax):
    #get discrete colormap
    cmap = plt.get_cmap('jet', (vmax - vmin))
    # set limits .5 outside true range
    mat = plt.matshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    #tell the colorbar to tick at integers
    cax = plt.colorbar(mat, )
    plt.savefig(filename)

class Simulator():
    def __init__(self, parent):
        self.widget = GLWidget(None)
        self.widget.resize(640, 480)
        self.widget.show()
        self.widget.maskCreated.connect(self.sendMask)
        self.learningModel = InitTrain()
        self.learningModel.initialtrain()
    def sendMask(self, mask):
        learned_reward = self.learningModel.phasetrain(mask, 4)
        print(learned_reward)
        #self.widget.setRoverPosition(50,80)
        # discrete_matshow(learned_reward, filename='maskedrewards.png', vmin=learned_reward.min(),vmax=learned_reward.max())


if __name__ == '__main__':

    app = QApplication(sys.argv)
    simul = Simulator(None)

    sys.exit(app.exec_())
