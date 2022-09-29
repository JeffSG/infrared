import math
import numpy as np
import re

skipNum = 10
avgNum = 3
burstThreshold = 0.13
cloudBurstPercentThreshold = 0.65
cloudSlopeThreshold = 1.2

skipTailingPoint = 90

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
	r = 0
	for i in range(dataCount):
		v = a * x[i] + b
		r += (v - y[i]) * (v - y[i])
	r = math.sqrt(r / dataCount)
	return a, b, r

# find the index of burst
# burst position is where the value exceeds the average of last avgNum points with the burstThreshold
def findBurstPos(data):
	dataSize = data.shape[0]
	for pos in range(skipNum + 1, dataSize):
		avg = np.average(data[pos + 1 - avgNum : pos + 1])
		diff = data[pos] - avg
		if burstThreshold <= diff:
			return pos
	return dataSize - 1

# determine if this is cloudy of burst
def cloudWithBurst(data, burstPos):
	dataSize = data.shape[0]
	return burstPos <= dataSize * cloudBurstPercentThreshold

# determine if this is cloudy with graduate increasing
def cloudWithSlope(data, burstPos, baseSlope):
	slope = float(data[burstPos] - data[skipNum]) / (burstPos - skipNum)
	slopeRatio = slope / baseSlope
	return cloudSlopeThreshold < slopeRatio

# determine if this is cloudy due to above base value
def cloudAboveBase(data, baseValue):
	dataSize = data.shape[0]
	pos = dataSize - 1
	for i in range(dataSize):
		if baseValue < data[i]:
			pos = i
			break
	return pos <= dataSize * cloudAboveBasePercentThreshold
