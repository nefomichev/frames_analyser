import cv2
import numpy as np
from PIL import Image
from db_proto import insert_into_db
import os
import time
from statistics import median
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
    image = image.astype(np.int32)
    previous_frame = image[0]

    while success:
        success, image = cap.read()
        if not success:
            break
        image = image.astype(np.int32)
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC)/100) # 1ms -- 1 frame
        if timestamp in timestamp_mas:
            cv2.imwrite("%s/frame%d.bmp" % (FRAME_FOLDER, timestamp), image)  # save frame as bmp file
            current_frame = image
            norm = int(np.linalg.norm(previous_frame - current_frame)) # get diff between two frames
            frames_norms.append((timestamp, norm, np.median(current_frame))) # median bad works, ToDO -- changed it
            previous_frame = current_frame
            timestamp_mas.remove(timestamp) # for sure that 1ms -- 1 frame
            if timestamp%1000==0:
                print("--------TIMESTAMP {0} FROM {1} SAVED, {2:.2f}s passed".format(timestamp,len(timestamp_mas), time.time()-time_start))
    return(frames_norms)

def norms_analysis(frames_norms, movie_name):
    temp_mas = []
    for i in range(len(frames_norms)-1):
        i+=1
        if frames_norms[i-1][1]==0:
            continue
        dif = frames_norms[i][1]/frames_norms[i-1][1]
        temp_mas.append([movie_name, frames_norms[i][0], frames_norms[i][1], dif, frames_norms[i][2]])
    insert_into_db(temp_mas)
    print("_______")