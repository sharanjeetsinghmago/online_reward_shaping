#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:24:38 2019
@author: shohei
"""

import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_toolkits.axes_grid1.colorbar import colorbar
import cv2

def color_detect(img): # assign reward value: -1
    # transform to HSV color space
    # Hue [0, 179], Saturation [0, 255], Value [0, 255]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #stars
    hsv_min_star = np.array([29,255,255])
    hsv_max_star = np.array([29,255,255])
    mask_star = cv2.inRange(hsv, hsv_min_star, hsv_max_star)

    # red region 1
    hsv_min_red = np.array([0, 127, 0])
    hsv_max_red = np.array([30, 255, 255])
    mask1_red = cv2.inRange(hsv, hsv_min_red, hsv_max_red)
    # red region 2
    hsv_min_red = np.array([150, 127, 0])
    hsv_min_red = np.array([179, 255, 255])
    mask2_red = cv2.inRange(hsv, hsv_min_red, hsv_max_red)

    # light gray region 1
    hsv_min_lgray = np.array([0, 0, 160])
    hsv_max_lgray = np.array([100, 20, 255])
    mask1_lgray = cv2.inRange(hsv, hsv_min_lgray, hsv_max_lgray)
    # light gray region 2
    hsv_min_lgray = np.array([10, 0, 120])
    hsv_max_lgray = np.array([20, 50, 180])
    mask2_lgray = cv2.inRange(hsv, hsv_min_lgray, hsv_max_lgray)

    # dark gray region
    hsv_min_dgray = np.array([85, 0, 0])
    hsv_max_dgray = np.array([140, 140, 140])
    mask_dgray = cv2.inRange(hsv, hsv_min_dgray, hsv_max_dgray)

    # salmon pink region 1
    hsv_min_spink = np.array([0, 0, 110])
    hsv_max_spink = np.array([5, 110, 255])
    mask1_spink = cv2.inRange(hsv, hsv_min_spink, hsv_max_spink)
    # salmon pink region 2
    hsv_min_spink = np.array([175, 0, 110])
    hsv_max_spink = np.array([179, 110, 255])
    mask2_spink = cv2.inRange(hsv, hsv_min_spink, hsv_max_spink)

    # white region
    hsv_min_white = np.array([0, 0, 200])
    hsv_max_white = np.array([360, 255, 255])
    mask_white = cv2.inRange(hsv, hsv_min_white, hsv_max_white)

    # yellow region
    hsv_min_yellow = np.array([0, 75, 120])
    hsv_max_yellow = np.array([60, 150, 200])
    mask_yellow = cv2.inRange(hsv, hsv_min_yellow, hsv_max_yellow)

    # green region
    hsv_min_green = np.array([100, 150, 100])
    hsv_max_green = np.array([140, 255, 200])
    mask_green = cv2.inRange(hsv, hsv_min_green, hsv_max_green)

    return mask_star, mask1_red+mask2_red, mask1_lgray+mask2_lgray, mask_dgray, mask1_spink+mask2_spink, mask_white, mask_yellow, mask_green

def image2reward(image_file, matvals=True):

    # initialization
    if matvals == True:
        img = image_file
    else:
        img = cv2.imread(image_file)

    rewardMatrix = np.zeros((img.shape[0], img.shape[1]))

    # extract specific color pixels (each mask * has 966*1048 pixels)
    mask_star, mask_red, mask_lgray, mask_dgray, mask_spink, mask_white, mask_yellow, mask_green = color_detect(img)
    #print(mask_red.shape, mask_lgray.shape, mask_dgray.shape, mask_spink.shape)

    # from each mask *, extract the color regions
    index_star = np.vstack((np.where(mask_star == 255)[0], np.where(mask_star == 255)[1]))
    index_red = np.vstack((np.where(mask_red == 255)[0], np.where(mask_red == 255)[1]))
    index_lgray = np.vstack((np.where(mask_lgray == 255)[0], np.where(mask_lgray == 255)[1]))
    index_dgray = np.vstack((np.where(mask_dgray == 255)[0], np.where(mask_dgray == 255)[1]))
    index_spink = np.vstack((np.where(mask_spink == 255)[0], np.where(mask_spink == 255)[1]))
    index_white = np.vstack((np.where(mask_white == 255)[0], np.where(mask_white == 255)[1]))
    index_yellow = np.vstack((np.where(mask_yellow == 255)[0], np.where(mask_yellow == 255)[1]))
    index_green = np.vstack((np.where(mask_green == 255)[0], np.where(mask_green == 255)[1]))

    # add reward points to the initial reward heatmap (np.zeros((img.shape[0], img.shape[1])))
    for i in range(index_star.shape[1]):
        rewardMatrix[index_star[0][i]][index_star[1][i]] = 50

    for i in range(index_yellow.shape[1]):
        rewardMatrix[index_yellow[0][i]][index_yellow[1][i]] = 1

    for i in range(index_red.shape[1]):
        rewardMatrix[index_red[0][i]][index_red[1][i]] = -5

    for i in range(index_dgray.shape[1]):
        rewardMatrix[index_dgray[0][i]][index_dgray[1][i]] = -3

    for i in range(index_spink.shape[1]):
        rewardMatrix[index_spink[0][i]][index_spink[1][i]] = -2

    for i in range(index_lgray.shape[1]):
        rewardMatrix[index_lgray[0][i]][index_lgray[1][i]] = 10

    for i in range(index_white.shape[1]):
        rewardMatrix[index_white[0][i]][index_white[1][i]] = 2

    for i in range(index_green.shape[1]):
        rewardMatrix[index_green[0][i]][index_green[1][i]] = 5

    return rewardMatrix

def goals(image_file):

    # get the reward matrix
    rewardMatrix = image2reward(image_file)

    # from "pixel coordinate" to "xy coordinate"
    rewardMatrix = rewardMatrix.T

    # initialization (grids)
    # grid configuration
    minx = 0.0; maxx = 2400.0
    miny = 0.0; maxy = 2400.0;
    greso = 2.0

    # robot states
    # initial start
    start = np.array([greso*25+greso/2, greso*25+greso/2])

    # initial goal index
    goal = np.array([greso*100+greso/2, greso*850+greso/2])

    xgrid_show, ygrid_show = np.mgrid[minx:maxx+greso:greso, miny:maxy+greso:greso]

    #plot
    fig = plt.figure(figsize=(10,10))
    ax1 = fig.add_subplot(111)
    ax1.set_xlim(minx - 1, maxx + 1); ax1.set_ylim(miny - 1, maxy + 1)
    ax1.set_aspect('equal')
    ax1.set_xlabel('x [m]'); ax1.set_ylabel('y [m]')
    ax1.set_title('Initial Heat Map in Atacama Desert')
    im1 = ax1.pcolor(xgrid_show, ygrid_show, rewardMatrix, cmap='jet', vmin=-5.0, vmax=10.0)
    ax1_divider = make_axes_locatable(ax1)
    cax1 = ax1_divider.append_axes("right", size="7%", pad="2%")
    fig.colorbar(im1, cax=cax1)
    ax1.plot(start[0], start[1], c='lime', marker='x')
    ax1.plot(goal[0], goal[1], c='gold', marker='o')
    plt.savefig('../img/image2reward_with_rrt.png')

def main():

    # image2reward('../img/atacama.png')
    goals('../img/atacama_texture.jpg')

if __name__ == '__main__':
    main()