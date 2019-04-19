from PyQt5.QtGui import QColor, QVector3D, QMatrix4x4

class Camera():
    delta_y = 0.001
    def __init__(self, position):
        self.Up = QVector3D(0., 1., 0.)
        self.position = position
        self.viewType = 0 #(0 : 1st Person, 1: 3rd Person, 3: Free)
        self.Direction = QVector3D(0., 0., 1.)

    def getViewMatrix(self, roverPosition):
        view = QMatrix4x4()
        if(self.viewType == 0):
            view.lookAt(roverPosition, roverPosition + self.Direction, self.Up)
        elif(self.viewType == 1):
            view.lookAt(self.position, roverPosition, self.Up)
        elif(self.viewType == 2):
            view.lookAt(self.position, self.position + self.Direction, self.Up)


        return view

    def scroll(self, angleDelta):
        self.position.setY(self.position.y() - self.delta_y * angleDelta)

    def setViewType(self, value):
        self.viewType = value

    def processMouseMovement(self, dx, dy):
        pass
    def processInput():
        pass