from PIL import Image
import numpy as np
from OpenGL.GL import *
import cv2 as cv

def ReadTexture(filename):
    # PIL can open BMP, EPS, FIG, IM, JPEG, MSP, PCX, PNG, PPM
    # and other file types.  We convert into a texture using GL.
    print('trying to open', filename)
    try:
        image = Image.open(filename).transpose(Image.FLIP_TOP_BOTTOM)
    except IOError as ex:
        print('IOError: failed to open texture file')
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1
    print('opened file: size=', image.size, 'format=', image.format)
    imageData = (np.array(list(image.getdata()), np.uint8))
    

    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1],
        0, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    image.close()
    return textureID

def ReadHeightMap(filename):
    # PIL can open BMP, EPS, FIG, IM, JPEG, MSP, PCX, PNG, PPM
    # and other file types.  We convert into a texture using GL.
    print('trying to open', filename)
    try:
        image = cv.imread(filename,-1)
    except IOError as ex:
        print('IOError: failed to open texture file')
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return -1
    imageData = np.flip(np.array(image, dtype='float32'),0)/65535.0
    print("read height map")
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R16, imageData.shape[0], imageData.shape[1],
        0, GL_RED, GL_FLOAT, imageData)

    return textureID

def NumpyTexture(textureId, numpyArray):
    glBindTexture(GL_TEXTURE_2D, textureId)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, numpyArray.shape[0], numpyArray.shape[1],
        0, GL_RGB, GL_UNSIGNED_BYTE, numpyArray)
# def ReadHeightMap(rewardMap):
#     pass
    # imageData = np.array(rewardMap, dtype='float32')/65535.0
    # print("read height map")
    # textureID = glGenTextures(1)
    # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.size[0], image.size[1],
    #     0, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    # return textureID
