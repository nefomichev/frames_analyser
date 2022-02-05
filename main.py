import time
import sys
import os
from video_proto import norms_analysis, create_frames
from db_proto import drop_data

if __name__ == '__main__':
    if len(sys.argv)<2:
        print('INSERT MOVIE TITLE')
        exit()

    MOVIE_NAME = sys.argv[1]

    if not os.path.isfile('data/%s' % MOVIE_NAME):
        print('THERE IS NOT FILE data/%s exists' % MOVIE_NAME)
        exit()

    timestamp = time.time()
    drop_data(MOVIE_NAME) # Entities should not be multiplied beyond necessity
    print('_________\nSTARTING GET FRAMES FROM MOVIE %s' %MOVIE_NAME) # get frame norms
    a = create_frames('data/%s' % MOVIE_NAME, timestamp)
    norms_analysis(a, MOVIE_NAME) # get diffs between frames
    print("TIME: ", time.time() - timestamp)
    print('_________\nEND')
