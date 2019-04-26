import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from color2reward import image2reward
import cv2


def discrete_matshow(data, filename, vmin, vmax):
    #get discrete colormap
    cmap = plt.get_cmap('jet', (vmax - vmin))
    # set limits .5 outside true range
    mat = plt.matshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    #tell the colorbar to tick at integers
    cax = plt.colorbar(mat, )
    plt.savefig(filename)

def colorcoord(img):
    imgmat = cv2.imread(img)

    rwd, yellowidx = image2reward(imgmat)

    # discrete_matshow(rwd, filename='atacamafullrewards/AArwdsall.png', vmin=rwd.min(), vmax=rwd.max())

    return yellowidx

starscoord = colorcoord('../img/atacamastarsonly2001.png')