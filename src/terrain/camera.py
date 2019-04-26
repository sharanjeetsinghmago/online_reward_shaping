from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4
from math import *
import numpy as np
import cv2 as cv

class Camera():
    yaw = -90.0
    pitch = 0.0
    speed = 1.0
    sensitivity = 0.1
    zoom = 45.0
    WORLD_UP = QVector3D(0., 1., 0.)
    delta_y = 0.001

    def __init__(self, position):
        self.Up = QVector3D(0., 1., 0.)
        self.position = position
        self.viewType = 0 #(0 : 1st Person, 1: 3rd Person, 3: Free)
        self.Front = QVector3D(0., 0., 1.)
        self.Right = QVector3D.crossProduct(self.Front, self.WORLD_UP)
        self.ReadHeightMap('textures/atacama_height2.png')
        self.updateCameraVectors()

    def getViewMatrix(self, roverPosition):
        view = QMatrix4x4()
        view.lookAt(self.position, self.position + self.Front, self.Up)

        return view

    def updateCameraVectors(self):
        front = QVector3D();
        front.setX(cos(radians(self.yaw)) * cos(radians(self.pitch)))
        front.setY(sin(radians(self.pitch)))
        front.setZ(sin(radians(self.yaw)) * cos(radians(self.pitch)))
        front.normalize()
        self.Front = front

        self.Right = QVector3D.crossProduct(self.Front, self.WORLD_UP)
        self.Right.normalize()
        self.Up = QVector3D.crossProduct(self.Right, self.Front)
        self.Up.normalize()

    def scroll(self, angleDelta):
        self.position.setY(self.position.y() - self.delta_y * angleDelta)

    def setViewType(self, value):
        self.viewType = value

    def processMouseMovement(self, dx, dy):
        xoffset = dx * self.sensitivity
        yoffset = dy * self.sensitivity

        self.yaw -= xoffset
        self.pitch += yoffset

        if (self.pitch>89.0):
            self.pitch = 89.0
        elif(self.pitch < -89.0):
            self.pitch = -89.0

        
        self.updateCameraVectors()

    def processKeyboard(self, direction, deltaTime):
        velocity = self.speed
        if(direction == 'F'):
            self.position += self.Front * velocity
        elif(direction == "B"):
            self.position -= self.Front * velocity
        elif(direction == "L"):
            self.position -= self.Right * velocity
        elif(direction == "R"):
            self.position += self.Right * velocity
        # print(int(self.imageData.shape[0] * (0.5 * self.position.z() + 0.5) ))
        # print(int(0.5 * self.position.x() + 0.5))
        i = round(self.imageData.shape[0] - self.imageData.shape[0] * ((0.5 * self.position.z()/4000.5) + 0.5) )
        j = round( self.imageData.shape[1] * ((0.5 * self.position.x()/4000.5) + 0.5) )
        self.position.setY(0.015625 * self.imageData[i,j] + 2.0)

    def processInput():
        pass

    def ReadHeightMap(self, filename):
        print('trying to open', filename)
        try:
            image = cv.imread(filename,-1)
        except IOError as ex:
            print('IOError: failed to open texture file')
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return -1
        self.imageData = np.array(image, dtype='float32')
        print("read height map")
        # print(self.imageData)