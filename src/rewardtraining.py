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

        self.sgdclass = SGDClassifier(warm_start=True)

    def initialtrain(self):

        # unroll the images for classification
        origdwnchannnels = self.img.reshape((self.img.shape[0] * self.img.shape[1]),
                                                    self.img.shape[2])
        origdwnrwdsunrolled = self.img.ravel()

        # stochastic gradient descent classifier
        self.sgdclass.fit(origdwnchannnels, origdwnrwdsunrolled)

    def unroll(self, image):

        unrolledimg = image.reshape((image.shape[0] * image.shape[1]), image.shape[2])
        return unrolledimg

    def phasetrain(self, mask, runval):

        if runval == 0:
            maskedrwd = self.rwdtrans0*mask
            maskedimg = self.imgtrans0*mask[:, :, None]
        elif runval == 1:
            maskedrwd = self.rwdtrans1*mask
            maskedimg = self.imgtrans1*mask[:, :, None]
        elif runval == 2:
            maskedrwd = self.rwdtrans2*mask
            maskedimg = self.imgtrans2*mask[:, :, None]
        elif runval == 3:
            maskedrwd = self.rwdtrans3*mask
            maskedimg = self.imgtrans3*mask[:, :, None]
        else:
            maskedrwd = self.rwd_stars * mask
            maskedimg = self.imgstars * mask[:, :, None]


        unrolledrwd = maskedrwd.ravel()
        unrolledimg = self.unroll(maskedimg)


        self.sgdclass.partial_fit(unrolledimg, unrolledrwd,
                                  classes=np.unique(unrolledrwd))

        roverrwds_unrolled = self.sgdclass.predict(unrolledimg)
        roverrwds = roverrwds_unrolled.reshape(maskedimg.shape[0], maskedimg.shape[1])

        nonzeromaskidx = np.nonzero(mask)
        self.rwd_orig[nonzeromaskidx] = roverrwds[nonzeromaskidx]

        return self.rwd_orig

## TEST

# # mask = np.random.binomial(size=(1001,1001), n=1, p=0.5)
# mask = np.zeros((1001,1001))
# mask[100:500, 100:500] = 1
# rewards = InitTrain().phasetrain(mask=mask, runval=4)
#
# def discrete_matshow(data, filename, vmin, vmax):
#     #get discrete colormap
#     cmap = plt.get_cmap('jet', (vmax - vmin))
#     # set limits .5 outside true range
#     mat = plt.matshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
#     #tell the colorbar to tick at integers
#     cax = plt.colorbar(mat, )
#     plt.savefig(filename)
#
# discrete_matshow(rewards, filename='maskedrewards.png', vmin=rewards.min(),
#                      vmax=rewards.max())