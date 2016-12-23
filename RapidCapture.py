'''
Created on Dec 16, 2016
@author: pfreyerm
'''
import time
import datetime
import threading
from time import sleep
from picamera import PiCamera
from fractions import Fraction
from io import BytesIO

frames = 10 

class GainControl(threading.Thread):
    def __init__(self):
        super(GainControl, self).__init__()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        
    def run(self):
        while running:
            sleep(1)
            camera.shutter_speed = camera.shutter_speed  + 1000
            print datetime.datetime.now().time()

camera = PiCamera(resolution=(1920, 1088))
camera.framerate = Fraction(1, 6)
camera.iso = 200
sleep(15)
camera.exposure_mode = 'off'
camera.shutter_speed = 1000
camera.still_stats = True
# g = camera.awb_gains
# camera.awb_mode = 'off'
# camera.awb_gains = g
start = time.time()
running = True
# gc = GainControl()
camera.capture_sequence(['image%02d.jpg' % i for i in range(frames)], burst=True)


finish = time.time()
print('Captured %d frames at %.2ffps in %.2fs' % (
    frames,
    frames / (finish - start), (finish - start)))
running = False



if __name__ == '__main__':
    pass