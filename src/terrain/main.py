#!/usr/bin/env python

import sys
import math

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4
from PyQt5.QtWidgets import *
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
import numpy as np

from camera import Camera
from terrain import Terrain
# import Rover
try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "OpenGL samplebuffers",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)


class GLWidget(QGLWidget):
    GL_MULTISAMPLE = 0x809D
    rot = 0.0
    lastMousePos = None
    def __init__(self, parent, f):
        super(GLWidget, self).__init__(f, parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.list_ = []
        self.width = 640.0
        self.height = 480.0
        self.startTimer(40)
        self.setWindowTitle("Sample Buffers")
        self.fov = 60.0

    def initializeGL(self):
        GL.glClearColor(0.50, 0.50, 0.50, 1.0)
        self.projection = QMatrix4x4()
        self.projection.perspective(self.fov, self.width / self.height, 0.01, 100)
        self.cameraPos = QVector3D(0.0, 0.1, 0.001)
        self.terrainPos = QVector3D(0.0, 0.0, 0.0)
        self.roverPos = QVector3D(0.0, 0.0, 0.0)
        print(GL.glGetString(GL.GL_VERSION))
        self.camera = Camera(self.cameraPos)
        self.terrain = Terrain(self.terrainPos)
        # self.rover = Rover(roverPos)

    def resizeGL(self, w, h):
        self.width = float(w)
        self.height = float(h)
        GL.glViewport(0, 0, w, h)
        self.projection = QMatrix4x4()
        self.projection.perspective(self.fov, (self.width / self.height), 0.01, 100)


    def paintGL(self):
        GL.glClearColor(0.90, 0.90, 0.90, 1.0)

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GLWidget.GL_MULTISAMPLE)
       
        self.view = self.camera.getViewMatrix(self.roverPos)
        self.terrain.draw(self.projection, self.view)
        # self.rover.draw(self.perspective, view)


        # self.qglColor(Qt.black)
        # self.renderText(-0.35, 0.4, 0.0, "Multisampling enabled")
        # self.renderText(0.15, 0.4, 0.0, "Multisampling disabled")

    def mousePressEvent(self, event):
        print("clicked")
        viewport = np.array(GL.glGetIntegerv(GL.GL_VIEWPORT))
        cursorX = event.x()
        cursorY = event.y()
        winX = float(cursorX)
        winY = float(viewport[3] - cursorY)
        
        # obtain Z position
        winZ = GL.glReadPixels(winX, winY, 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);
        
        winVector = QVector3D(winX, winY, winZ)
        print(winVector)
        object_coord = self.terrain.getObjectCoord(winVector, self.projection, self.view, viewport)
        print(object_coord)
        # raw_z = GL.glReadPixels(winX, winY, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT);
        # print(raw_z)

    def mouseMoveEvent(self, event):
        print(event.pos())
        if(event.button() == Qt.LeftButton):
            if(self.lastMousePos is not None):
                dx = event.x() - self.lastMousePos.x()
                dy = event.y() - self.lastMousePos.y()
                self.camera.processMouseMovement(dx,dy)
            self.lastMousePos = event.pos()
        elif(event.button() == Qt.MiddleButton):
            # Dont use this : doesnt work well with trackpads
            print("Middle")
        elif(event.button() == Qt.RightButton):
            print("Right")

    def mouseReleaseEvent(self, event):
        print("Mouse Released")
        
    def wheelEvent(self, event):
        self.camera.scroll((event.angleDelta().y()))

    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.camera.setViewType(0)
        elif event.key() == Qt.Key_2:
            self.camera.setViewType(1)
        elif event.key() == Qt.Key_3:
            self.camera.setViewType(2)
            
        
    def timerEvent(self, event):
        self.update()
    

if __name__ == '__main__':

    app = QApplication(sys.argv)

    # OpenGL Widget setup
    f = QGLFormat()
    f.setSampleBuffers(True)
    f.setVersion(3,3)
    f.setProfile(QGLFormat.CoreProfile)
    QGLFormat.setDefaultFormat(f)

    if not QGLFormat.hasOpenGL():
        QMessageBox.information(None, "OpenGL samplebuffers",
                "This system does not support OpenGL.")
        sys.exit(0)

    widget = GLWidget(None, f)

    if not widget.format().sampleBuffers():
        QMessageBox.information(None, "OpenGL samplebuffers",
                "This system does not have sample buffer support.")
        sys.exit(0)

    widget.resize(640, 480)
    # widget.show()
    window = QWidget()
    window.setGeometry(1,1,640,480)
    grid = QGridLayout()
    grid.setColumnStretch(0, 3)
    grid.setColumnStretch(1, 1)
    grid.addWidget(widget, 0, 0, 10, 1)

    fovLabel = QLabel("Field Of View")
    fovSlider = QSlider(Qt.Horizontal)
    grid.addWidget(fovLabel, 0, 1)
    grid.addWidget(fovSlider, 1, 1)
    fovSlider.setRange(25.0, 180.0)
    window.setLayout(grid)
    window.show()

    sys.exit(app.exec_())
