from pyrr import Matrix44, Vector3

class Camera():
    delta_y = 0.001
    def __init__(self, position):
        self.Up = Vector3([0., 1., 0.])
        self.position = position
        self.viewType = 0 #(0 : 1st Person, 1: 3rd Person, 3: Free)
        self.Direction = Vector3([0., 0., 1.])

    def getViewMatrix(self, roverPosition):
        if(self.viewType == 0):
            view = Matrix44.look_at(roverPosition, roverPosition + self.Direction, self.Up)
        elif(self.viewType == 1):
            view = Matrix44.look_at(self.position, roverPosition, self.Up)
        elif(self.viewType == 2):
            view = Matrix44.look_at(self.position, self.position + self.Direction, self.Up)


        return view

    def scroll(self, angleDelta):
        self.position.y = self.position.y - self.delta_y * angleDelta

    def setViewType(self, value):
        self.viewType = value

    def processMouseMovement(self, dx, dy):
        pass
    def processInput():
        pass