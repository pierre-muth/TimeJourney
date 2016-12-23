'''
Created on Dec 17, 2016
@author: pfreyerm
'''


import io
import time
import picamera
import picamera.array
from time import sleep
from fractions import Fraction

with picamera.PiCamera() as camera:
    camera.resolution = (128, 128) 
    camera.framerate = Fraction(1, 6)
    sleep(15)
    camera.still_stats = True
    stream = io.BytesIO()
    start = time.time()
    for foo in camera.capture_continuous(stream, burst = True, format='rgb'):
        # Truncate the stream to the current position (in case
        # prior iterations output a longer image)
        stream.truncate()
        stream.seek(0)
        print stream.read(50)
        stream.seek(0)
         
        if (time.time() - start) > 20:
            break


if __name__ == '__main__':
    pass