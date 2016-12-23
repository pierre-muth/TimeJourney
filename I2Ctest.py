'''
Created on Dec 20, 2016

@author: pfreyerm
'''

import smbus
import time

# Get I2C bus
bus = smbus.SMBus(1)

# MCP3426 address, 0x68(104)
# Send configuration command
#        0x10(16)    Continuous conversion mode, Channel-1, 12-bit Resolution
bus.write_byte(0x68, 0x18)

# MCP3426 address, 0x68(104)
# Read data back from 0x00(0), 2 bytes
# light_adc MSB, light_adc LSB
data = bus.read_i2c_block_data(0x68, 0x00, 2)

# Convert the data to 16-bits
light_adc = data[0] * 256 + data[1]
bus.write_byte(0x68, 0x18)

# Output data to screen
print "Digital Value of Analog Input is : %d" %light_adc
print data


if __name__ == '__main__':
    pass