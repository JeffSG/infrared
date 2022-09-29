import os
import re
import shutil
import sys

import jcloud

baseFolder = sys.argv[1]
outSunnyFolder = sys.argv[2]
outCloudyFolder = sys.argv[3]
confidentNum = 3
histCloudy = [False] * confidentNum
curConfidentIndex = 0

if os.path.isdir(outSunnyFolder):
	shutil.rmtree(outSunnyFolder)
os.makedirs(outSunnyFolder, exist_ok = True)
if os.path.isdir(outCloudyFolder):
	shutil.rmtree(outCloudyFolder)
os.makedirs(outCloudyFolder, exist_ok = True)

def finalDecision():
	num = 0
	for histResult in histCloudy:
		if histResult:
			num += 1
	return confidentNum < num * 2

bFirst = True
for name in os.listdir(baseFolder):
	if name.endswith('.txt'):
		dataFilePath = os.path.join(baseFolder, name)
		dataFile = open(dataFilePath, 'r')
		rawData = dataFile.readline()[:-1]
		dataFile.close()
		pattern = r' +'
		frameRawData = re.split(pattern, rawData)
		frameData = jcloud.initData(frameRawData)
		burstPos = jcloud.findBurstPos(frameData)
		isBurst = jcloud.cloudWithBurst(frameData, burstPos)
		if bFirst:
			baseSlope = float(frameData[burstPos] - frameData[jcloud.skipNum]) / (burstPos - jcloud.skipNum)
			bFirst = False
			isSlope = False
		elif not isBurst:
			isSlope = jcloud.cloudWithSlope(frameData, burstPos, baseSlope)
		curDecision = isBurst or isSlope
		histCloudy[curConfidentIndex] = curDecision
		if curConfidentIndex < confidentNum - 1:
			curConfidentIndex += 1
		else:
			curConfidentIndex = 0
		result = finalDecision()
		fileName = name[:-3] + 'jpg'
		sourceFile = os.path.join(baseFolder, fileName)
		if result:
			targetFile = os.path.join(outCloudyFolder, fileName)
		else:
			targetFile = os.path.join(outSunnyFolder, fileName)
		shutil.copyfile(sourceFile, targetFile)
		#print('{}\t{}\t{}\t{}\t{}'.format(name, str(burstPos), str(isBurst), str(curDecision), str(result)))
