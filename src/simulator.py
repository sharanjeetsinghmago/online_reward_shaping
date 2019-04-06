import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

class testing_func(QDialog):
    def __init__(self):
        super(testing_func,self).__init__()
        loadUi('../uis/simulator.ui',self)
        self.setWindowTitle('Simulator')
        self.button_map.clicked.connect(self.on_button_map_clicked)
        self.button_heatmap.clicked.connect(self.on_button_heatmap_clicked)
    @pyqtSlot()
    def on_button_map_clicked(self):
    #    self.label1.setText('Welcome :'+self.lineEdit.text())
        self.graphicsView.setScene(scene)

    def on_button_heatmap_clicked(self):
        self.graphicsView_2.setScene(scene_2)


app=QApplication(sys.argv)
widget=testing_func()
widget.show()


scene = QGraphicsScene()
pic = QPixmap('atacama.png')

scene.addPixmap(pic)
#scene.resize(50,50);

scene_2 = QGraphicsScene()
scene_2.addPixmap(QPixmap('image2reward_with_rrt.jpg'))


sys.exit(app.exec_())
