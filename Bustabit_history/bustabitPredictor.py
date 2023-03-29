import pickle
import numpy as np

def labels(value):
  if value < 2:
    return 0
  else:
    return 1
def preprocess(value):
	return float(value[:-1])
def realTimePredictor(series, path):
	series = list(map(preprocess, series))
	series = map(labels,series)
	series = np.array(list(series))
	with open(path, "rb") as myFile:
		Model = pickle.load(myFile)
	listToStr = ''.join(map(str, series))
	Str0 = listToStr+"0"
	Str1 = listToStr+"1"
	Str0_1 = [Model[Str0],Model[Str1]]
	maxval = max(Str0_1)
	if maxval == Model[Str0]:
		return 0 #default is to predict zero
	else:
		return 1

#length of list should be 13 or variable - model dependent
#path of the model
predicted_value = realTimePredictor(['1.1x','1.2x','4x','4x','4x','4x','4x','4x','1x','1x','3x','3x','1x'],"mySavedDict.txt")
print(predicted_value)