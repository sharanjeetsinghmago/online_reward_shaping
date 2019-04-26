import sys
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import scipy

from image2reward import *;
from image2reward_with_a_star import a_star_planning;

class simulation(QDialog):
    def __init__(self):
        super(simulation,self).__init__()
        loadUi('../uis/simulator.ui',self)
        self.setWindowTitle('Simulator')

        self.button_heatmap.clicked.connect(self.heatmap_clicked)
        self.button_generate_heatmap.clicked.connect(self.generate_heatmap_clicked)
        self.button_generate_path.clicked.connect(self.generate_path_clicked)

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
        self.sx = 50.0       # [m]
        self.sy = 50.0       # [m]
        # goal coordinate
        self.gx = 1550.0      # [m]
        self.gy = 1770.0     # [m]
        # grid property
        self.greso = 2.0     # [m]
        # robot size (assume the robot size is 2*2 meters)
        self.rs = 2.0        # [m]
        # size of the whole environment (values are calculated based on image pixels)
        self.minx = 0.0      # [m]
        self.maxx = 2096.0   # [m]
        self.miny = 0.0      # [m]
        self.maxy = 1932.0   # [m]

        self.xwidth = round(self.maxx - self.minx)

        self.rx = 0.0
        self.ry = 0.0


        self.graphics()

        self.scene1.mousePressEvent = lambda event:imageMousePress(event,self)
        self.scene1.mouseMoveEvent = lambda event:imageMouseMove(event,self)
        self.scene1.mouseReleaseEvent = lambda event:imageMouseRelease(event,self)

    def graphics(self):



        self.scene1 = QGraphicsScene()
        #self.scene1.addPixmap(QPixmap('../img/atacama.png'))
        self.graphicsView.setScene(self.scene1)

        makeTruePlane(self)

    @pyqtSlot()


    def heatmap_clicked(self):
        print("<<Loading Heatmap>>")
        scene_2.addPixmap(QPixmap('../img/image2reward_with_rrt.png'))
        self.graphicsView_2.setScene(scene_2)
        print("<<Loading heatmap complete>>")

    def generate_heatmap_clicked(self):
        print("<<Generating Heatmap>>")
        self.rewardMatrix = image2reward('../img/atacamaTexture1001.png')
        print("<<Heatmap Generated>>")
        #print("<<Loading Heatmap>>")
        #scene_2.addPixmap(QPixmap(self.rewardMatrix))
        #self.graphicsView_2.setScene(scene_2)
        #print("<<Loading Heatmap complete>>")

    def generate_path_clicked(self):
        self.rx, self.ry = a_star_planning(self.sx, self.sy, self.gx, self.gy, self.rewardMatrix, self.greso, self.rs, self.xwidth, self.minx, self.miny, self.maxx, self.maxy)
        


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

scene_2 = QGraphicsScene()
#scene_2.addPixmap(QPixmap('../img/image2reward_with_rrt.jpg'))


sys.exit(app.exec_())
