import cv2
from sklearn.linear_model import SGDClassifier
from color2reward import image2reward
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import numpy as np

class InitTrain(object):

    'Takes in png image'

    def __init__(self):
        self.img = cv2.imread('atacamaTexture1001.png')
        self.imgstars = cv2.imread('1001atacamastarsall.png')

        self.imgtrans0 = cv2.imread('1001atacamastarsopc20.png')
        self.imgtrans1 = cv2.imread('1001atacamastarsopc40.png')
        self.imgtrans2 = cv2.imread('1001atacamastarsopc60.png')
        self.imgtrans3 = cv2.imread('1001atacamastarsopc80.png')

        self.rwdtrans0 = image2reward(self.imgtrans0)
        self.rwdtrans1 = image2reward(self.imgtrans1)
        self.rwdtrans2 = image2reward(self.imgtrans2)
        self.rwdtrans3 = image2reward(self.imgtrans3)

        self.rwd_orig = image2reward(self.img)
        self.rwd_stars = image2reward(self.imgstars)

        self.sgdclass = SGDClassifier()

    def initialtrain(self):


        # unroll the images for classification
        origdwnchannnels = self.img.reshape((self.img.shape[0] * self.img.shape[1]),
                                                    self.img.shape[2])
        origdwnrwdsunrolled = self.img.ravel()

        # stochastic gradient descent classifier
        self.sgdclass = self.sgdclass.fit(origdwnchannnels, origdwnrwdsunrolled)

    def unroll(self, image):

        unrolledimg = image.reshape((image.shape[0] * image.shape[1]), image.shape[2])
        return unrolledimg

    def phasetrain(self, mask, runval):

        maskedrwd = (self.rwdtrans + str(runval))*mask
        maskedimg = (self.imgtrans + str(runval))*mask

        unrolledrwd = self.unroll(maskedrwd)
        unrolledimg = self.unroll(maskedimg)

        unrolledrwdidx = np.nonzero(unrolledrwd)
        unrolledimgidx = np.nonzero(unrolledimg)

        self.sgdclass = self.sgdclass(warm_start=True).partial_fit(unrolledimgidx, unrolledrwdidx,
                                                                   classes=np.unique(unrolledrwd))

        roverrwds = self.sgdclass.predict(unrolledimg)
        # maskedroverrwds = roverrwds*mask

        nonzeromaskidx = np.nonzero(mask)
        self.rwd_orig[nonzeromaskidx] = roverrwds[nonzeromaskidx]

        return self.rwd_orig
