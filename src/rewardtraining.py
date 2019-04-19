import cv2
from sklearn.linear_model import SGDClassifier
from color2reward import image2reward
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import numpy as np


def resize_crop(img, dwnszval=5, saveimages=False, prec='orig'):

    # crop the image so its divisible by downsampling value
    dim1, dim2 = img.shape[0], img.shape[1]
    dim1cropped = (dim1//dwnszval)*dwnszval
    dim2cropped = (dim2//dwnszval)*dwnszval
    cropped_img = img[0:dim1cropped][0:dim2cropped][:]

    # downsample
    resized_img = cv2.resize(cropped_img, (dim2cropped//dwnszval, dim1cropped//dwnszval))  # format is widthxheight
    reproduced_img = cv2.resize(resized_img, (dim2cropped, dim1cropped))

    # pil image just for visualizing
    if saveimages:
        cv2.imwrite(prec + 'croppedimage.png', cropped_img)
        cv2.imwrite(prec + 'resizedimage.png', resized_img)
        cv2.imwrite(prec + 'reproducedimage.png', reproduced_img)

    return cropped_img, resized_img, reproduced_img

def discrete_matshow(data, filename, vmin, vmax):
    #get discrete colormap
    cmap = plt.get_cmap('jet', (vmax - vmin))
    # set limits .5 outside true range
    mat = plt.matshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    #tell the colorbar to tick at integers
    cax = plt.colorbar(mat, )
    plt.savefig(filename)

def unroll(img):
    unrolledimg = img.reshape((img.shape[0] * img.shape[1]), img.shape[2])
    return unrolledimg

def phaselearning(phasetrans, phaseopaque, phaseno):
    pactualrwd_trans = image2reward(phasetrans)
    pactualrwd_opaque = image2reward(phaseopaque)
    ptactrwds_unrolled = pactualrwd_trans.ravel()
    pt_unrolled = unroll(phasetrans)
    sgdclass = SGDClassifier(warm_start=True).partial_fit(pt_unrolled, ptactrwds_unrolled,
                                                          classes=np.unique(ptactrwds_unrolled))
    ptroverrwds_unrolled = sgdclass.predict(pt_unrolled)
    ptroverrwds = ptroverrwds_unrolled.reshape(phasetrans.shape[0], phasetrans.shape[1])
    discrete_matshow(ptroverrwds, filename='phase' + str(phaseno) + 'roverrwds.png', vmin=ptroverrwds.min(),
                     vmax=ptroverrwds.max())
    discrete_matshow(pactualrwd_opaque, filename='phase' + str(phaseno) + 'actualrwds.png', vmin=pactualrwd_opaque.min(),
                     vmax=pactualrwd_opaque.max())

def initial_train():

    # original and starred images
    imgorig = 'atacama.png'
    origimg = cv2.imread(imgorig)
    starredimgorig = 'atacamastarry.png'
    starredimg = cv2.imread(starredimgorig)

    # cropped, resized, and downsampled images
    orig_cropped, orig_downsampled, orig_recreated = resize_crop(origimg, dwnszval=10, saveimages=True, prec='orig')
    star_cropped, star_downsampled, star_recreated = resize_crop(starredimg, dwnszval=10, saveimages=True, prec='star')

    # get the rewards for the downsampled and actual images
    rwd_orig = image2reward(orig_cropped)
    rwd_dwnsamporig = image2reward(orig_downsampled)
    rwd_starred = image2reward(star_cropped)

    # create the reward maps
    discrete_matshow(rwd_orig, filename='rwdsorig.png', vmin=rwd_orig.min(), vmax=rwd_orig.max())
    discrete_matshow(rwd_dwnsamporig, filename='rwdsorigdwn.png', vmin=rwd_dwnsamporig.min(), vmax=rwd_dwnsamporig.max())
    discrete_matshow(rwd_starred, filename='rwdsstarred.png', vmin=rwd_starred.min(), vmax=rwd_starred.max())

    # unroll the images for classification
    origdwnchannnels = orig_downsampled.reshape((orig_downsampled.shape[0]*orig_downsampled.shape[1]), orig_downsampled.shape[2])
    origdwnrwdsunrolled = rwd_dwnsamporig.ravel()

    # stochastic gradient descent classifier
    sgdclass = SGDClassifier().fit(origdwnchannnels, origdwnrwdsunrolled)

    # test on an actual image (unaltered/original)
    testimg = origimg[200:900, 200:900, :]
    testimg_unroll = testimg.reshape((testimg.shape[0] * testimg.shape[1]), testimg.shape[2])
    testrwds_unroll = sgdclass.predict(testimg_unroll)
    testrwds = testrwds_unroll.reshape(testimg.shape[0], testimg.shape[1])
    actrwds = image2reward(testimg)
    discrete_matshow(testrwds, filename='testrwdsfromrover.png', vmin=testrwds.min(), vmax=testrwds.max())
    discrete_matshow(actrwds, filename='testrwdsactual.png', vmin=actrwds.min(), vmax=actrwds.max())

    # test on starred
    testimgstarred = starredimg[200:900, 200:900, :]
    testimgstarred_unroll = testimgstarred.reshape((testimgstarred.shape[0]*testimgstarred.shape[1]), testimgstarred.shape[2])
    testrwdsstarred_unroll = sgdclass.predict(testimgstarred_unroll)
    testrwdsstarred = testrwdsstarred_unroll.reshape(testimgstarred.shape[0], testimgstarred.shape[1])
    actrwdsstarred = image2reward(testimgstarred)
    actrwdsstarred_unroll = actrwdsstarred.ravel()
    discrete_matshow(testrwdsstarred, filename='testrwdsfromrover_starred.png', vmin=testrwdsstarred.min(), vmax=testrwdsstarred.max())
    discrete_matshow(actrwdsstarred, filename='testrwdsactual_starred.png', vmin=actrwdsstarred.min(), vmax=actrwdsstarred.max())

    ## THIS IS WHERE THE SKETCHED IMAGE WOULD COME IN

    # phase 1
    phase1trans = cv2.imread('phase1_trans.png')
    phase1opaque = cv2.imread('phase1_opaque.png')
    phaselearning(phase1trans, phase1opaque, phaseno=1)

    # phase 2
    phase2trans = cv2.imread('phase2_trans.png')
    phase2opaque = cv2.imread('phase2_opaque.png')
    phaselearning(phase2trans, phase2opaque, phaseno=2)

    # phase 3
    phase3trans = cv2.imread('phase3_trans.png')
    phase3opaque = cv2.imread('phase3_opaque.png')
    phaselearning(phase3trans, phase3opaque, phaseno=3)

    # phase 4
    phase4trans = cv2.imread('phase4_trans.png')
    phase4opaque = cv2.imread('phase4_opaque.png')
    phaselearning(phase4trans, phase4opaque, phaseno=4)

    # phase 5
    phase5trans = cv2.imread('phase5_trans.png')
    phase5opaque = cv2.imread('phase5_opaque.png')
    phaselearning(phase5trans, phase5opaque, phaseno=5)

    # phase 6
    phase6trans = cv2.imread('phase6_trans.png')
    phase6opaque = cv2.imread('phase6_opaque.png')
    phaselearning(phase6trans, phase6opaque, phaseno=6)


# run
initial_train()