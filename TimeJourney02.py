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

#I2C bus init
bus = smbus.SMBus(1)

#vars
stack_mode_request = True
light_adc = 0
im_nb = 0
shot_min = 0
shot_max = 0
shot_mean = 0
start_time = time.time()

def light_meas(camera):
    global stack_mode_request
    
    # read I2C ADC
    data = bus.read_i2c_block_data(0x68, 0x00, 2)
    light_adc = data[0] * 256 + data[1]
    if light_adc >= 0x7FFF :
        light_adc = light_adc - 0xFFFF
    light_adc += 0x7FFF
    bus.write_byte(0x68, 0x18)
    
    print('i2c light: %d' % (light_adc))
    
    #camera setings
    if light_adc < 6800:
        camera.iso = 800
        camera.shutter_speed = 6000000
        stack_mode_request = False
    elif light_adc < 8500:
        camera.iso = 100
        camera.shutter_speed = 6000000
        stack_mode_request = True
    elif light_adc < 10000:
        camera.iso = 100
        camera.shutter_speed = 2000000
        stack_mode_request = True
    elif light_adc < 17000:
        camera.iso = 100
        camera.shutter_speed = 500000
        stack_mode_request = True
    elif light_adc < 27000:
        camera.iso = 100
        camera.shutter_speed = 100000
        stack_mode_request = True
    elif light_adc < 40000:
        camera.iso = 100
        camera.shutter_speed = 20000
        stack_mode_request = True
    elif light_adc < 50000:
        camera.iso = 100
        camera.shutter_speed = 5000
        stack_mode_request = True
    elif light_adc < 55000:
        camera.iso = 100
        camera.shutter_speed = 2000
        stack_mode_request = True
    else:
        camera.iso = 100
        camera.shutter_speed = 500
        stack_mode_request = True
        
    fd = open('light_meas.csv','a')
    fd.write('%d, %d, %d, %d, %d, %d, %f, %f\n' %
             (shot_min, shot_max, shot_mean, light_adc, camera.exposure_speed, camera.iso, camera.awb_gains[0], camera.awb_gains[1]))
    fd.close()

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:

        #camera setup
        camera.resolution = (WIDTH, HEIGHT)
        camera.still_stats = True
        camera.framerate = Fraction(1, 6)
        camera.exposure_mode = 'night'
        
        #jpeg quality
        quality_val = 95

        #val init
        last_start = time.time()
        pixBuffer = np.zeros( (HEIGHT, WIDTH, 3) )
        
        stack_mode_request = True
        stack_mode = True
        
        while True:
            light_meas(camera)
            stack_mode = stack_mode_request
            #let some time especially is long expoure time
            sleep(8)
            for foo in camera.capture_continuous(output, format='rgb', burst=True):
                # Averaging or maximizing ?
                if stack_mode:
                    pixBuffer += output.array
                else:
                    np.copyto(pixBuffer, output.array, where=output.array>pixBuffer)
                
                shot_min = np.min(output.array)
                shot_max = np.max(output.array)
                shot_mean = np.mean(output.array)
                
                print('Shot mean: %d, min: %d, max: %d' % (shot_mean, shot_min, shot_max))
                print('a_g %d, d_g: %d, awb_g: %f, %f, S_Speed %d us' % 
                      (camera.analog_gain, camera.digital_gain, camera.awb_gains[0], camera.awb_gains[1], camera.exposure_speed))

                output.truncate(0)

                light_meas(camera)

                if time.time() - last_start > DELAY :
                    #normalizing
                    pixBuffer -= np.min(pixBuffer)
                    pixBuffer *= (255/np.max(pixBuffer)) 
                    
                    #saving jpeg
                    im = Image.fromarray(pixBuffer.astype(np.uint8))
                    im.save('tj02-'+str(im_nb).zfill(6)+'.jpg', 'JPEG', quality=quality_val)
                    print('----'+str(im_nb).zfill(6)+'---- stack_mode_request:'+str(stack_mode_request)+' stack_mode:'+str(stack_mode))
                    
                    #init
                    last_start = time.time()
                    im_nb += 1
                    pixBuffer.fill(0)
                    
                    #do we have to change iso and stacking mode ?
                    #we must stop to change iso
                    if stack_mode_request != stack_mode: 
                        break
                
if __name__ == '__main__':
    pass