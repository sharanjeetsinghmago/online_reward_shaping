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

def bindHeightMap(heightMap):
    textureID = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R16, heightMap.shape[0], heightMap.shape[1],
        0, GL_RED, GL_FLOAT, heightMap/65535.0)

    return textureID

def bindRewardMap(textureId, rewardMap):
    glBindTexture(GL_TEXTURE_2D, textureId)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, rewardMap.shape[0], rewardMap.shape[1],
        0, GL_RGB, GL_UNSIGNED_BYTE, rewardMap)

