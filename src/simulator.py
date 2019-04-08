import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from image2reward import *;


class testing_func(QDialog):
    def __init__(self):
        super(testing_func,self).__init__()
        loadUi('../uis/simulator.ui',self)
        self.setWindowTitle('Simulator')
        self.button_map.clicked.connect(self.map_clicked)
        self.button_heatmap.clicked.connect(self.heatmap_clicked)
        self.button_generate_heatmap.clicked.connect(self.generate_heatmap_clicked)

    @pyqtSlot()
    def map_clicked(self):
        self.graphicsView.setScene(scene)

    def heatmap_clicked(self):
        scene_2.addPixmap(QPixmap('image2reward_with_rrt.jpg'))
        self.graphicsView_2.setScene(scene_2)

    def generate_heatmap_clicked(self):
        image2reward('atacama.png')


app=QApplication(sys.argv)
widget=testing_func()
widget.show()


scene = QGraphicsScene()
pic = QPixmap('../img/atacama.png')

scene.addPixmap(pic)
#scene.resize(50,50);

scene_2 = QGraphicsScene()
scene_2.addPixmap(QPixmap('image2reward_with_rrt.jpg'))


sys.exit(app.exec_())
