import math
import numpy as np
import re

skipTailingPoint = 90

tempThreshold = 9.6
percentThreshold = 0.6

varTempThreshold = 9.5
errorThreshold = 0.3
slopeThreshold = 1.6

def initData(rawData):
	data = np.asfarray(rawData)
	sortedData = np.sort(data)
	return sortedData

def linearFit(data):
	dataCount = data.shape[0] - skipTailingPoint
	x = np.array(range(dataCount))
	y = data[:-skipTailingPoint]
	z = np.polyfit(x, y, 1)
	a = z[0]
	b = z[1]
	return a, b

def isCloudy(data, a, b):
	dataCount = data.shape[0] - skipTailingPoint
	targetCount = 0
	errCount = 0
	r = 0
	for i in range(dataCount):
		refValue = a * i + b
		if refValue < data[i]:
			r += (data[i] - refValue) * (data[i] - refValue)
		if refValue + tempThreshold < data[i]:
			targetCount += 1
	p = float(targetCount) / dataCount
	r = math.sqrt(r / dataCount)
	return p, r

def isCloudyV2(data, a, b):
	dataCount = data.shape[0] - skipTailingPoint
	vt = 0
	la, lb = linearFit(data)
	r = 0
	for i in range(dataCount):
		refValue = a * i + b
		if refValue < data[i]:
			vt += (data[i] - refValue) * (data[i] - refValue)
		localValue = la * i + lb
		if localValue < data[i]:
			r += (data[i] - localValue)
	vt = math.sqrt(vt / dataCount)
	r /= float(dataCount)
	return vt, r, la / a

