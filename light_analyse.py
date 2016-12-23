'''
Created on Dec 17, 2016
@author: pierremuth.wordpress.com
'''

import picamera
import picamera.array
from fractions import Fraction
from PIL import Image
import numpy as np
import smbus
import time
from time import sleep

WIDTH = 2560
HEIGHT = 1440
# WIDTH = 640
# HEIGHT = 384

SHUTTER_SPEEDS = (100, 200, 500, 
                  1000, 2000, 5000, 
                  10000, 20000, 50000, 
                  100000, 200000, 500000, 
                  1000000, 2000000, 6000000, 
                  6000000, 6000000, 6000000, 6000000)

ISOS = (100, 100, 100, 
        100, 100, 100, 
        100, 100, 100, 
        100, 100, 100, 
        100, 100, 100, 
        100, 200, 400, 800)

AVERAGING = (False, False, False, 
             False, False, False, 
             False, False, False, 
             False, False, False, 
             False, False, False, 
             False, False, False, True) 

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
        #camera setup
        camera.resolution = (WIDTH, HEIGHT)
        camera.still_stats = True
        camera.framerate = Fraction(1, 6)
        camera.iso = 100
        camera.exposure_mode = 'night'
        camera.shutter_speed = 100
        #jpeg quality
        quality_val = 95

        #I2C bus init
        bus = smbus.SMBus(1)
        
        #val init
        last_start = time.time()
        
        im_nb = 0
        shot_min = 0
        shot_max = 0
        shot_mean = 0
        
        stack_averaging = False
        
        while True :
            camera.iso = ISOS[im_nb%19]
            camera.shutter_speed = SHUTTER_SPEEDS[im_nb%19]
            sleep(8)

            for foo in camera.capture_continuous(output, format='rgb', burst=True):
                shot_min = np.min(output.array)
                shot_max = np.max(output.array)
                shot_mean = np.mean(output.array)
                print('Shot mean: %d, min: %d, max: %d' % (shot_mean, shot_min, shot_max))
                
                # read I2C ADC
                data = bus.read_i2c_block_data(0x68, 0x00, 2)
                light_adc = data[0] * 256 + data[1]
                if light_adc >= 0x7FFF :
                    light_adc = light_adc - 0xFFFF
                light_adc += 0x7FFF
                bus.write_byte(0x68, 0x18)

                #save image
                im = Image.fromarray(output.array)
                im.save('tja-L'+str(light_adc/1000).zfill(2)+'-P'+str(im_nb%19).zfill(2)+'.jpg', 'JPEG', quality=quality_val)
                output.truncate(0)
    
                print('analog_gain %d, digital_gain: %d, awb_gains: %f, %f, S_Speed %d us, i2c_light: %d' % 
                      (camera.analog_gain, camera.digital_gain, camera.awb_gains[0], camera.awb_gains[1], 
                       camera.exposure_speed, light_adc))
                
                fd = open('light_meas.csv','a')
                fd.write('%d, %d, %d, %d, %d, %d, %f, %f, %d, %d\n' %
                         (shot_min, shot_max, shot_mean, light_adc, camera.exposure_speed, 
                          camera.iso, camera.awb_gains[0], camera.awb_gains[1], time.time(), (im_nb%19) ))
                fd.close()
                
                im_nb += 1    
                if camera.iso != ISOS[im_nb%19] : break
                camera.shutter_speed = SHUTTER_SPEEDS[im_nb%19]
                sleep(1)
            
if __name__ == '__main__':
    pass