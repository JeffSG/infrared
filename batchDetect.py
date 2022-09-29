import os

dataPath = 'data\\fullSet'
clasPath = 'data\\classification'

for path in os.listdir(dataPath):
	if os.path.isdir(dataPath + '\\' + path) and 10 == len(path):
		cmd = 'python cloudDetect2.py .\\data\\typical\\2022-09-18-18-30-08.txt {}\\{} {}\\{}-clear {}\\{}-cloudy'.format(dataPath, path, clasPath, path, clasPath, path)
		print(path)
		os.system(cmd)
