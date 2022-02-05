import cv2
import numpy as np
from PIL import Image
from db_proto import insert_into_db
import os
import time
from statistics import median
from skimage.metrics import structural_similarity

import sys

from scipy.linalg import norm
from scipy import sum, average

def to_grayscale(arr):
    if len(arr.shape) == 3:
        return average(arr, -1)
    else:
        return arr

def rebin(a, shape=None):
    if not shape:
        shape = [max(int(x * 0.5), 1) for x in a.shape]
    sh = shape[0], a.shape[0] // shape[0] , shape[1], a.shape[1] // shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def crop_center(img):
    # for future tests
    y,x = img.shape
    size = min(y,x)
    startx = x//2-(size//2)
    starty = y//2-(size//2)    
    return img[starty:starty+size,startx:startx+size]

def compress(img):
    return rebin(to_grayscale(img))

def create_frames(movietitle, time_start):
    #init
    cap = cv2.VideoCapture(movietitle)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    timestamp_mas = [i for i in range(int(10 * duration))] # make a mas with timestamps
    frames_norms = []

    # print_stats
    print(movietitle, "duration:", duration)
    print(movietitle, "resolution:", cap.get(3), "x", cap.get(4))
    print(movietitle, "fps:",  fps)
    print(movietitle, "frame_count:", frame_count)
    print(movietitle, "frame_savings:", len(timestamp_mas))

    #make directory to save frames
    FRAME_FOLDER = movietitle.split('.')[0]
    if not os.path.exists(FRAME_FOLDER):
        os.mkdir(FRAME_FOLDER)


    #start get frames
    success, image = cap.read()
    image = compress(image.astype(np.int32))
    previous_frame = image

    while success:
        success, image = cap.read()
        if not success:
            break
        image = compress(image.astype(np.int32))
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC)/100) # 1ms -- 1 frame
        if timestamp in timestamp_mas:
            cv2.imwrite("%s/frame%d.bmp" % (FRAME_FOLDER, timestamp), image)  # save frame as bmp file
            current_frame = image
            print(previous_frame.shape, current_frame.shape)
            norm = int(np.linalg.norm(previous_frame - current_frame)) # get diff between two frames
            m_norm = compare_images(previous_frame, current_frame)
            frames_norms.append((timestamp, norm, np.median(current_frame) , m_norm)) # median bad works, ToDO -- changed it
            previous_frame = current_frame
            timestamp_mas.remove(timestamp) # for sure that 1ms -- 1 frame
            if timestamp%1000==0:
                print("--------TIMESTAMP {0} FROM {1} SAVED, {2:.2f}s passed".format(timestamp,len(timestamp_mas), time.time()-time_start))
    return(frames_norms)

def compare_images(img1, img2):
    return structural_similarity(img1, img2, full=True)[0]


def norms_analysis(frames_norms, movie_name):
    temp_mas = []
    for i in range(len(frames_norms)-1):
        i+=1
        if frames_norms[i-1][1]==0:
            continue
        dif = frames_norms[i][1]/frames_norms[i-1][1]
        m_diff = frames_norms[i][3]/frames_norms[i-1][3]
        temp_mas.append([movie_name, frames_norms[i][0], frames_norms[i][1], dif, frames_norms[i][2], frames_norms[i][3]])
    insert_into_db(temp_mas)
    print("_______")
    
