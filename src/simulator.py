import sys
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from PyQt5.QtWidgets import QMessageBox

import scipy
import time
import numpy



from color2reward import *;
from a_star_with_costmap import a_star_planning;

from simulator3d import GLWidget
from rewardtraining import InitTrain


class simulation(QDialog):
    def __init__(self):
        super(simulation,self).__init__()
        loadUi('../uis/simulator.ui',self)
        self.setWindowTitle('Simulator')

        self.button_heatmap.clicked.connect(self.heatmap_clicked)
        self.button_generate_heatmap.clicked.connect(self.generate_heatmap_clicked)
        self.button_generate_path.clicked.connect(self.generate_path_clicked)
        self.button_drive.clicked.connect(self.drive_clicked)
        self.button_send_mask.clicked.connect(self.send_mask_clicked)

        #Sketching Params
        self.sketchListen=False;
        self.sketchingInProgress = False;
        self.allSketches = {};
        self.allSketchNames = [];
        self.allSketchPaths = [];
        self.allSketchPlanes = {};
        self.sketchLabels = {};
        self.sketchDensity = 3; #radius in pixels of drawn sketch points

        img = cv2.imread('../img/atacamaTexture1001.png')
        self.rewardMatrix = np.zeros((img.shape[0], img.shape[1]))

        #A* Params
        # initialization of the 2D grid environment
        # start coordinate
        self.sx = 57.0       # [m]
        self.sy = 65.0       # [m]
        # goal coordinate
        self.gx = 80.0      # [m]
        self.gy = 100.0     # [m]
        # grid property
        self.greso = 1.0     # [m]
        # robot size (assume the robot size is 2*2 meters)
        self.rs = 1.0        # [m]
        # size of the whole environment (values are calculated based on image pixels)
        self.minx = 0.0      # [m]
        self.maxx = 1001.0   # [m]
        self.miny = 0.0      # [m]
        self.maxy = 1001.0   # [m]

        self.xwidth = round(self.maxx - self.minx)

        self.ry = np.loadtxt('rx.txt')
        self.rx = np.loadtxt('ry.txt')

        self.ryhalf = np.loadtxt('rx_orig_firsthalf')
        self.rxhalf = np.loadtxt('ry_orig_firsthalf')

        self.rystarhalf = np.loadtxt('rx_stars_secondhalf')
        self.rxstarhalf = np.loadtxt('ry_stars_secondhalf')

        self.i = 0
        self.j = 0
        self.passid = 0

        self.fuel = 100

        self.nov_det = 0

        self.igx = self.sx
        self.igy = self.sy

        self.actualReward = 0.0

        self.graphics()



        self.label_reward.setText(str(0))

        self.label_fuel_value.setText(str(self.fuel))

    #    self.scene1.mousePressEvent = lambda event:imageMousePress(event,self)
    #    self.scene1.mouseMoveEvent = lambda event:imageMouseMove(event,self)
    #    self.scene1.mouseReleaseEvent = lambda event:imageMouseRelease(event,self)

        self.widget = GLWidget(None)
        self.widget.resize(640, 480)
        self.widget.show()
        self.widget.maskCreated.connect(self.sendMask)
        self.learningModel = InitTrain()
        self.learningModel.initialtrain()

    def graphics(self):

        self.scene1 = QGraphicsScene()
        self.scene1.addPixmap(QPixmap('../img/atacamaTexture500'))
        self.graphicsView.setScene(self.scene1)

        #makeTruePlane(self)

    def sendMask(self, mask):
        print("Testing Working")
        print(mask)
        mask = numpy.flip(mask,0)
        print("mask flipped")
        self.rewardMatrix = self.learningModel.phasetrain(mask, 4)

    @pyqtSlot()

    def show_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("Popup")
        msg.setText("This is the text ")

        x = msg.exec_()

    def send_mask_clicked(self):
        mask = np.random.binomial(size=(1001,1001), n=1, p=0.5)
        mask = np.zeros((1001,1001))
        mask[250:1000, 400:1000] = 1
        self.rewardMatrix = self.learningModel.phasetrain(mask, 4)

    def heatmap_clicked(self):
        print("<<Loading Heatmap>>")
        scene_2.addPixmap(QPixmap('../img/heatmap.png'))
        self.graphicsView_2.setScene(scene_2)
        print("<<Loading heatmap complete>>")

    def generate_heatmap_clicked(self):
        print("<<Generating Heatmap>>")
        self.rewardMatrix = image2reward('../img/atacamaTexture1001.png',False)
        print("<<Heatmap Generated>>")
        #print("<<Loading Heatmap>>")
        #scene_2.addPixmap(QPixmap(self.rewardMatrix))
        #self.graphicsView_2.setScene(scene_2)
        #print("<<Loading Heatmap complete>>")

    def generate_path_clicked(self):

        print("<<Generating Path>>")
        self.rx, self.ry, self.costMatrix, self.accumReward = a_star_planning(self.sx, self.sy, self.gx, self.gy, self.rewardMatrix, self.greso, self.rs, self.xwidth, self.minx, self.miny, self.maxx, self.maxy)
        #time.sleep(10)

        #self.ry = np.loadtxt('init_pathy.txt')
        #self.rx = np.loadtxt('init_pathx.txt')

        print("<<Path Generated>>")

        self.label_reward.setText(str(self.accumReward))

        #self.label_reward.setText(str(866.0))


        print("<<discrete plot start>>")
    #    discrete_matshow(self.rewardMatrix, 'pika_test.png', vmin=self.rewardMatrix.min(), vmax=self.rewardMatrix.max())

        #get discrete colormap

        vmin=self.rewardMatrix.min()
        vmax=self.rewardMatrix.max()

        cmap = plt.get_cmap('plasma', (vmax - vmin))
        # set limits .5 outside true range
        mat = plt.matshow(self.rewardMatrix, cmap=cmap, vmin=vmin, vmax=10)

        plt.plot(self.rx,self.ry, '-k', linewidth=3)

        #tell the colorbar to tick at integers
        cax = plt.colorbar(mat, )
        plt.savefig('../img/initial_path.png')

        print("<<discrete plot finish>>")


        print("<<loading path map")
        scene_2.addPixmap(QPixmap('../img/initial_path.png'))
        self.graphicsView_2.setScene(scene_2)
        print("<<loading path map finished>>")

        self.rx = np.flip(self.rx)
        self.ry = np.flip(self.ry)

        np.savetxt("init_pathx.txt",self.rx,delimiter=',')
        np.savetxt("init_pathy.txt",self.ry,delimiter=',')




    def drive_clicked(self):

        print("i =")
        print(self.i)

        self.passid = self.passid + 1



        self.sx = self.igx
        self.sy = self.igy

        #self.igx = self.rx[self.rx.size - self.i]
        #self.igy = self.ry[self.ry.size - self.i]

        vmin=self.rewardMatrix.min()
        vmax=self.rewardMatrix.max()

        cmap = plt.get_cmap('plasma', (vmax - vmin))
        # set limits .5 outside true range
        mat = plt.matshow(self.rewardMatrix, cmap=cmap, vmin=vmin, vmax=10)


        if ((self.i + 2) < self.rx.size):

            self.i = self.i + 2
            self.igx = self.rx[self.i]
            self.igy = self.ry[self.i]
            self.fuel = self.fuel - 2

        else:

            self.igx = self.gx
            self.igy = self.gy

            print("<<<<< Goal Reached >>>>>")

            msg = QMessageBox()
            msg.setWindowTitle("Popup")
            msg.setText("This is the text ")

            x = msg.exec_()



        plt.plot(self.rx,self.ry, '-k', linewidth=3)

        plt.plot(self.sx,self.sy, 'or',linewidth=5)


        print("Start Point")
        print("x =",self.sx)
        print("y =",self.sy)

        print("Goal Point")
        print("x =",self.igx)
        print("y =",self.igy)

        self.widget.setRoverPosition(self.sx,self.sy)

        lrx, lry, lcostMatrix, laccumReward = a_star_planning(self.sx, self.sy, self.igx, self.igy, self.rewardMatrix, self.greso, self.rs, self.xwidth, self.minx, self.miny, self.maxx, self.maxy)

        self.actualReward = self.actualReward + laccumReward;

        self.label_actual_reward.setText(str(self.actualReward))

        self.label_fuel_value.setText(str(self.fuel))

        print("Reward Collected =",laccumReward)

        # self.label_actual_reward.setText("TBD")

        #tell the colorbar to tick at integers
        cax = plt.colorbar(mat, )
        plt.savefig('../img/actual_path.png')

        scene_2.addPixmap(QPixmap('../img/actual_path.png'))
        self.graphicsView_2.setScene(scene_2)

'''
        if(self.i < self.rxhalf.size):

            self.i = self.i + 10
            self.igx = self.rxhalf[self.i]
            self.igy = self.ryhalf[self.i]

            plt.plot(self.rx,self.ry, '-k', linewidth=3)

            plt.plot(self.sx,self.sy, 'or',linewidth=5)

        else:

            self.j = self.j + 10
            self.igx = self.rxstarhalf[self.j]
            self.igy = self.rystarhalf[self.j]

            plt.plot(self.rx,self.ry, '-k', linewidth=3)

            plt.plot(self.rxstarhalf,self.rystarhalf, '-w', linewidth=1)

            plt.plot(self.sx,self.sy, 'or',linewidth=5)
'''

'''
def imageMousePress(QMouseEvent,wind):
    print("MouseClicked")
    wind.sketchingInProgress = True;
    name = 'xxx'
    if(name not in wind.allSketchPlanes.keys()):
        wind.allSketchPlanes[name] = wind.scene1.addPixmap(makeTransparentPlane(wind));
        #wind.objectsDrop.addItem(name);
        #wind.allSketchNames.append(name);

    else:
        planeFlushPaint(wind.allSketchPlanes[name],[]);


def imageMouseMove(QMouseEvent,wind):
    print("MouseMove")
    if(wind.sketchingInProgress):
        tmp = [int(QMouseEvent.scenePos().x()),int(QMouseEvent.scenePos().y())];

        print('x = ', QMouseEvent.scenePos().x(),' y = ', QMouseEvent.scenePos().y())

        #wind.allSketchPaths[-1].append(tmp);
		#add points to be sketched
        points = [];
        si = wind.sketchDensity;
        for i in range(-si,si+1):
            for j in range(-si,si+1):
                points.append([tmp[0]+i,tmp[1]+j]);

        name = 'xxx';
        planeAddPaint(wind.allSketchPlanes[name],points);



def imageMouseRelease(QMouseEvent,wind):
    print("MouseReleased")
    if(wind.sketchingInProgress):
        tmp = 'xxx'
        #wind.sketchName.clear();
        #wind.sketchName.setPlaceholderText("Sketch Name");

        #cost = wind.costRadioGroup.checkedId();
        #speed = wind.speedRadioGroup.checkedId();
        #wind.safeRadio.setChecked(True);
        #wind.nomRadio.setChecked(True);

        #wind.allSketches[tmp] = wind.allSketchPaths[-1];
        wind.sketchListen = False;
        wind.sketchingInProgress = False;
        #updateModels(wind,tmp,cost,speed);
'''

def makeTruePlane(wind):

	wind.trueImage = QPixmap('../img/atacamaTexture1001.png');
	wind.imgWidth = wind.trueImage.size().width();
	wind.imgHeight = wind.trueImage.size().height();

	wind.truePlane = wind.scene1.addPixmap(wind.trueImage);


def makeTransparentPlane(wind):

	testMap = QPixmap(wind.imgWidth,wind.imgHeight);
	testMap.fill(QtCore.Qt.transparent);
	return testMap;

def planeFlushPaint(planeWidget,points=[],col = None,pen=None):
	pm = planeWidget.pixmap();
	pm.fill(QColor(0,0,0,0));

	painter = QPainter(pm);
	if(pen is None):
		if(col is None):
			pen = QPen(QColor(0,0,0,255));
		else:
			pen = QPen(col);
	painter.setPen(pen)

	for p in points:
		painter.drawPoint(p[0],p[1]);
	painter.end();
	planeWidget.setPixmap(pm);

def updateModels(wind,tmp,cost,speed):
    pass

def planeAddPaint(planeWidget,points=[],col=None,pen=None):

	pm = planeWidget.pixmap();

	painter = QPainter(pm);
	if(pen is None):
		if(col is None):
			pen = QPen(QColor(0,0,0,255));
		else:
			pen = QPen(col);
	painter.setPen(pen)

	for p in points:
		painter.drawPoint(p[0],p[1]);
	painter.end();
	planeWidget.setPixmap(pm);

app=QApplication(sys.argv)
widget=simulation()
widget.show()

#simul = Simulator(None)

scene_2 = QGraphicsScene()
#scene_2.addPixmap(QPixmap('../img/image2reward_with_rrt.jpg'))


sys.exit(app.exec_())
