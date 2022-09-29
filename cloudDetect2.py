import os
import re
import shutil
import sys

import jcloud

def loadData(path):
	file = open(path, 'r')
	rawData = file.readline()[:-1]
	file.close()
	frameRawData = re.split(r' +', rawData)
	frameData = jcloud.initData(frameRawData)
	return frameData

refClearDataFile = sys.argv[1]
baseFolder = sys.argv[2]
outSunnyFolder = sys.argv[3]
outCloudyFolder = sys.argv[4]

if os.path.isdir(outSunnyFolder):
	shutil.rmtree(outSunnyFolder)
os.makedirs(outSunnyFolder, exist_ok = True)
if os.path.isdir(outCloudyFolder):
	shutil.rmtree(outCloudyFolder)
os.makedirs(outCloudyFolder, exist_ok = True)

refData = loadData(refClearDataFile)
a, b = jcloud.linearFit(refData)

for name in os.listdir(baseFolder):
	if name.endswith('.txt'):
		dataFilePath = os.path.join(baseFolder, name)
		frameData = loadData(dataFilePath)
		#p, r = jcloud.isCloudy(frameData, a, b)
		p, r, k = jcloud.isCloudyV2(frameData, a, b)
		result = p > jcloud.varTempThreshold or r > jcloud.errorThreshold or k > jcloud.slopeThreshold
		srcFileName = '%s.jpg' % (name[:-4])
		tarFileName = '%s_%f_%f_%f.jpg' % (name[:-4], p, r, k)
		sourceFile = os.path.join(baseFolder, srcFileName)
		if result:
			targetFile = os.path.join(outCloudyFolder, tarFileName)
		else:
			targetFile = os.path.join(outSunnyFolder, tarFileName)
		shutil.copyfile(sourceFile, targetFile)
		#print('{}\t{}\t{}\t{}\t{}'.format(name, str(burstPos), str(isBurst), str(curDecision), str(result)))
