#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 00:01:09 2019

@author: shohei
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_toolkits.axes_grid1.colorbar import colorbar
import cv2


"""
image2reward
"""
def color_detect(img): 
    # transform to HSV color space
    # Hue [0, 179], Saturation [0, 255], Value [0, 255]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # red region 1
    hsv_min_red = np.array([0, 127, 0])
    hsv_max_red = np.array([30, 255, 255])
    mask1_red = cv2.inRange(hsv, hsv_min_red, hsv_max_red)
    # red region 2
    hsv_min_red = np.array([150, 127, 0])
    hsv_min_red = np.array([179, 255, 255])
    mask2_red = cv2.inRange(hsv, hsv_min_red, hsv_max_red)
    
    # light gray region
    hsv_min_lgray = np.array([0, 0, 100])
    hsv_max_lgray = np.array([40, 60, 255])
    mask_lgray = cv2.inRange(hsv, hsv_min_lgray, hsv_max_lgray)
    
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
    
    return mask1_red+mask2_red, mask_lgray, mask_dgray, mask1_spink+mask2_spink

"""
a star algorithm
"""
class Node:
    
    def __init__(self, x, y, cost, pind):
        self.x = x
        self.y = y
        self.cost = cost
        self.pind = pind # parent index


def calc_obstacle_map(rewardMatrix):
    obmap = (rewardMatrix == -1)
    # print(obmap.shape) (1048, 966) 
    # print(obmap) ([[False, False, ..., False]...[False, ... , False]])
    
    return obmap

def get_motion_model():
    # motion primitive (column 0 & 1) + moving cost (column 2)
    motion = [[1, 0, 2],                # right
              [0, 1, 2],                # top 
              [-1, 0, 2],               # left
              [0, -1, 2],               # bottom
              [-1, -1, math.sqrt(2)],   # bottom left
              [-1, 1, math.sqrt(2)],    # top left
              [1, -1, math.sqrt(2)],    # bottom right
              [1, 1, math.sqrt(2)],     # top rihgt
              ]
    
    return motion    


# this function returns the 'key' of each openset component
def calc_index(node, xwidth, minx, miny):
    #return ((node.y - miny) / 2) * (xwidth/2 + 1) + (node.x - minx) / 2
    # the below equation will the same result from the above one but meaning is different...
    return ((node.y - miny) / 2 * xwidth) - 1 + (node.x - minx) / 2


# in this code, the heuristic is the distance between ngoal & corresponding openset component
def calc_heuristic(n1, n2):
    # w is the weight of heuristic. So, this is the tuning parameter of this algorithm.
    w = 1.0
    d = w * math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)
    
    return d

def verify_node(node, obmap, minx, miny, maxx, maxy):
    if node.x < minx:
        return False
    elif node.y < miny:
        return False
    elif node.x >= maxx:
        return False
    elif node.y >= maxy:
        return False
    
    if obmap[node.x][node.y]:
        return False
    
    return True


def calc_final_path(ngoal, closedset, greso):
    # generate the final path
    rx, ry = [ngoal.x * greso], [ngoal.y * greso]
    pind = ngoal.pind
    while (pind != -1):
        n = closedset[pind]
        rx.append(n.x * greso)
        ry.append(n.y * greso)
        pind = n.pind
    
    return rx, ry


def a_star_planning(sx, sy, gx, gy, rewardMatrix, greso, rs, xwidth, minx, miny, maxx, maxy):
    """
    sx:     start x coordinate [m]
    sy:     start y coordinate [m]
    gx:     goal x coordinate  [m]
    gy:     goal y coordinate  [m]
    rewardMatrix: represents the reward value of each grid (b/t -1 & 4)
    greso:  grid resolution  [m]
    rs:     robot size       [m]
    xwidth: x width [m]
    minx:   minimum x coordinate [m]
    miny:   minimum y coordinate [m]
    maxx:   maximum x coordinate [m]
    maxy:   maximum y coordinate [m]
    """
    
    """
    preparation
    """
    # initialize the start & goal nodes
    nstart = Node(math.floor(sx/greso), math.floor(sy/greso), 0.0, -1)
    ngoal = Node(math.floor(gx/greso), math.floor(gy/greso), 0.0, -1)
    
    # create an obstacle map (in this np.array, if obstacle -> True, else -> False)
    obmap = calc_obstacle_map(rewardMatrix)
    
    # get_motion_model returns the motion-with-cost model in this simulation
    motion = get_motion_model()
    
    # make empty dictionary for openset and closedset
    openset, closedset = dict(), dict()
    
    # openset is a gigantic 1D dictionary. 
    # in this dict, calc_index plays part in "key" connecting the node info (xy position, cost, & parent index)
    openset[calc_index(nstart, xwidth, minx, miny)] = nstart
    
    """
    loop
    """
    while (True):
        # find a calc_index whose total cost (cost + heuristic cost) is minimum from 'openset'
        # openset[o].cost = distance from current node to node in openset
        # calc_heuristc = heuristic cost
        c_id = min(openset, key=lambda o: openset[o].cost + calc_heuristic(ngoal, openset[o]))
        current = openset[c_id]
        
        # check the terminal condition
        if (current.x == ngoal.x) and (current.y == ngoal.y):
            print("Find goal")
            
            ngoal.pind = current.pind
            ngoal.cost = current.cost
            break
        
        # delete the key, c_id, from openset (dictionary)
        del openset[c_id]
        # add current with the key, c_id, to closedset (this is also a dictionary)
        closedset[c_id] = current
        
        # consider the surrounding nodes of current node
        for i, _ in enumerate(motion):
              # these nodes' parent is current node
              node = Node(current.x + motion[i][0],
                          current.y + motion[i][1],
                          current.cost + motion[i][2], c_id)
              
              # also calculate the calc_index about surrounding nodes
              n_id = calc_index(node, xwidth, minx, miny)  
              
              # if n_id is already in the closedset, just continue
              if n_id in closedset:
                  continue 
              
              # if the surrounding node is obstacle, this node will not be included to openset... 
              if not verify_node(node, obmap, minx, miny, maxx, maxy):
                  continue 
              
              # if n_id is not already in the closedset, add it to openset  
              if n_id not in openset:
                  openset[n_id] = node
              
              else:
                  # replace the parent index if the following condition is satisfied
                  if openset[n_id].cost >= node.cost:
                      openset[n_id] = node   
    
    """
    calculate the final path
    """
    rx, ry = calc_final_path(ngoal, closedset, greso)
      
    return rx, ry    


def main():
    #sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
    
    """
    image2reward 
    """
    # initialization of image and rewardMatrix
    image_file = '../img/atacama.png'
    img = cv2.imread(image_file)
    rewardMatrix = np.zeros((img.shape[0], img.shape[1]))
#    print(rewardMatrix.shape) # (966, 1048)
    
    # extract specific color pixels (each mask has 966*1048 pixels)
    mask_red, mask_lgray, mask_dgray, mask_spink = color_detect(img)

    # by using each mask, extract the specific color regions 
    index_red = np.vstack((np.where(mask_red == 255)[0], np.where(mask_red == 255)[1]))    
    index_lgray = np.vstack((np.where(mask_lgray == 255)[0], np.where(mask_lgray == 255)[1]))
    index_dgray = np.vstack((np.where(mask_dgray == 255)[0], np.where(mask_dgray == 255)[1]))
    index_spink = np.vstack((np.where(mask_spink == 255)[0], np.where(mask_spink == 255)[1]))

    # add reward values to the reward heatmap based on the above color (np.zeros((img.shape[0], img.shape[1])))
    for i in range(index_red.shape[1]):
        rewardMatrix[index_red[0][i]][index_red[1][i]] = -1
    
    for i in range(index_dgray.shape[1]): 
        rewardMatrix[index_dgray[0][i]][index_dgray[1][i]] = 2
    
    for i in range(index_spink.shape[1]):
        rewardMatrix[index_spink[0][i]][index_spink[1][i]] = 3

    for i in range(index_lgray.shape[1]):    
        rewardMatrix[index_lgray[0][i]][index_lgray[1][i]] = 4             

    # from "pixel coordinate" to "xy coordinate" 
    # below this line, we must use this 'rewardMatrix'
    rewardMatrix = rewardMatrix.T


    """
    a* algorithm
    """
    # initialization of the 2D grid environment
    # start coordinate
    sx = 50.0       # [m]
    sy = 50.0       # [m]
    # goal coordinate
    gx = 1550.0      # [m]
    gy = 1770.0     # [m]
    # grid property
    greso = 2.0     # [m]
    # robot size (assume the robot size is 2*2 meters)
    rs = 2.0        # [m]
    # size of the whole environment (values are calculated based on image pixels)
    minx = 0.0      # [m]
    maxx = 2096.0   # [m]
    miny = 0.0      # [m]
    maxy = 1932.0   # [m]
    
    xwidth = round(maxx - minx)
    #ywidth = round(maxy - miny)
    
    # execute a* algorithm which returns the optimal path
    rx, ry = a_star_planning(sx, sy, gx, gy, rewardMatrix, greso, rs, xwidth, minx, miny, maxx, maxy)

    """
    plot
    """
    xgrid_show, ygrid_show = np.mgrid[minx:maxx+greso:greso, miny:maxy+greso:greso] 
    
    fig = plt.figure(figsize=(10,10)) 
    ax1 = fig.add_subplot(111)
    ax1.set_xlim(minx - 1, maxx + 1); ax1.set_ylim(miny - 1, maxy + 1)
    ax1.set_aspect('equal')
    ax1.set_xlabel('x [m]'); ax1.set_ylabel('y [m]')
    ax1.set_title('Initial Heat Map in Atacama Desert with a* path plan')
    im1 = ax1.pcolor(xgrid_show, ygrid_show, rewardMatrix, cmap='jet', vmin=-1.0, vmax=4.0)
    ax1_divider = make_axes_locatable(ax1)
    cax1 = ax1_divider.append_axes("right", size="7%", pad="2%")
    fig.colorbar(im1, cax=cax1)
    ax1.plot(sx, sy, c='lime', marker='x')
    ax1.plot(gx, gy, c='gold', marker='o')
    ax1.plot(rx, ry, "-g")
    plt.savefig('../img/image2reward_with_a_star.jpg')
    
if __name__ == '__main__':
    main()    