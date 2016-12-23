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
DELAY = 300

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
        #camera setup
        camera.resolution = (WIDTH, HEIGHT)
        camera.still_stats = True
        camera.framerate = Fraction(1, 6)
        camera.iso = 800
        camera.exposure_mode = 'night'
        camera.shutter_speed = 6000000
        #jpeg quality
        quality_val = 95

        #I2C bus init
        bus = smbus.SMBus(1)
        
        #let some time especially is long expoure time
        sleep(10)

        #val init
        last_start = time.time()
        pixBuffer = np.zeros( (HEIGHT, WIDTH, 3) )
        
        im_nb = 0
        shot_min = 0
        shot_max = 0
        shot_mean = 0
        
        stack_mode_request = False

        for foo in camera.capture_continuous(output, format='rgb', burst=True):
            if stack_mode_request:
                pixBuffer += output.array
            else:
                np.copyto(pixBuffer, output.array, where=output.array>pixBuffer)
                
            shot_min = np.min(output.array)
            shot_max = np.max(output.array)
            shot_mean = np.mean(output.array)
            
            print('Shot mean: %d, min: %d, max: %d' % (shot_mean, shot_min, shot_max))
            output.truncate(0)

            if time.time() - last_start > DELAY :
                pixBuffer -= np.min(pixBuffer)
                pixBuffer *= (255/np.max(pixBuffer)) 
                
                im = Image.fromarray(pixBuffer.astype(np.uint8))
                im.save('tj-a-'+str(im_nb).zfill(6)+'.jpg', 'JPEG', quality=quality_val)
                print('------------'+str(im_nb).zfill(6)+'---------------')
                last_start = time.time()
                im_nb += 1
                pixBuffer.fill(0)
            
            # read I2C ADC
            data = bus.read_i2c_block_data(0x68, 0x00, 2)
            light_adc = data[0] * 256 + data[1]
            if light_adc >= 0x7FFF :
                light_adc = light_adc - 0xFFFF
            light_adc += 0x7FFF
            bus.write_byte(0x68, 0x18)

            print('analog_gain %d, digital_gain: %d, awb_gains: %f, %f, S_Speed %d us, i2c_light: %d' % 
                  (camera.analog_gain, camera.digital_gain, camera.awb_gains[0], camera.awb_gains[1], camera.exposure_speed, light_adc))
            
            fd = open('light_meas.csv','a')
            fd.write('%d, %d, %d, %d, %d, %d, %f, %f\n' %
                     (shot_min, shot_max, shot_mean, light_adc, camera.exposure_speed, camera.iso, camera.awb_gains[0], camera.awb_gains[1]))
            fd.close()
            
if __name__ == '__main__':
    pass