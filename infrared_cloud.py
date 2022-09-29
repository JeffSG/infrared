import cv2
import datetime
import math
import numpy as np
import re
import serial
import sys
import time
import os
import jimage

if len(sys.argv) < 2:
	exit('infrared.py <com port> <sample interval seconds>')

rawImgFactor = 16

curDate = datetime.datetime.now().strftime('%Y-%m-%d')
curPath = '.\\data\\' + curDate
os.makedirs(curPath, exist_ok = True)
imgPath = curPath
datPath = curPath
comPort = sys.argv[1]
try:
	intervalSec = int(sys.argv[2])
except:
	intervalSec = 60

def configAndOk (ser, cmd):
	ser.write(cmd.encode())
	data = ''
	while not 'OK\r\n' in data:
		data += ser.read().decode()

ser = serial.Serial()
ser.port = comPort
ser.baudrate = 460800
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 1

ser.open()
time.sleep(1)

# disable auto output, clear cache
print('clearing cache...', end='')
configAndOk(ser, '$SETP=7,0\r\n')
print('done')
time.sleep(1)

# turn off LED
print('turning off the LED...', end='')
configAndOk(ser, '$SETP=9,0\r\n')
print('done')
time.sleep(1)

while True:
	timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
	print('processing ' + timestamp, end = '')
	ser.write('$SETP=7,1\r\n'.encode())
    # skip OK
	ser.read(4)
	# skip MLX_TMP
	ser.read(9)
	data = ''
	while not 'MLX_TMP' in data:
        data += ser.read().decode()
	mlxPos = data.index('MLX_TMP')
	framedata = data[1:mlxPos - 2]
	pattern = r' +'
	values = re.split(pattern, framedata)
	dataFile = datPath + '\\' + timestamp + '.txt'
	with open(dataFile, 'w') as f:
		f.write(framedata)
		f.close()
	width = 32
	height = 24
	img = np.zeros([height, width], dtype = float)
	rawImg = np.zeros([height * rawImgFactor, width * rawImgFactor], dtype=float)
	for col in range(width):
		for row in range(height):
			v = float(values[row * width + col])
			img[row, col] = v
			for y in range(row * rawImgFactor, (row + 1) * rawImgFactor):
				for x in range(col * rawImgFactor, (col + 1) * rawImgFactor):
					rawImg[y, x] = v
	finalImg = jimage.generateImg(img)
	imgFile = imgPath + '\\' + timestamp + '.jpg'
	cv2.imwrite(imgFile, finalImg)
	finalRawImg = jimage.render(rawImg)
	rawImgFile = imgPath + '\\' + timestamp + '_raw.jpg'
	cv2.imwrite(rawImgFile, finalRawImg)
	print('...done.')
	time.sleep(1)
	configAndOk(ser, '$SETP=7,0\r\n')
	time.sleep(intervalSec)
ser.close()
