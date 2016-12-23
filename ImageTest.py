'''
Created on Dec 17, 2016

@author: pfreyerm
'''

# from io import BytesIO
# from time import sleep
# from picamera import PiCamera
# from PIL import Image

# # Create the in-memory stream
# stream = BytesIO()
# camera = PiCamera()
# camera.resolution = (128, 128)
# camera.start_preview()
# sleep(2)
# camera.capture(stream, format='rgb')
# # "Rewind" the stream to the beginning so we can read its content
# stream.seek(0)
# image = Image.from_rgb()


from PIL import Image
import numpy as np

data = np.random.random((100,100))

#Rescale to 0-255 and convert to uint8
rescaled = (255.0 / data.max() * (data - data.min())).astype(np.uint8)

im = Image.fromarray(rescaled)
im.save('test.png')

if __name__ == '__main__':
    pass