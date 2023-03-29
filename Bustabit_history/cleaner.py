# Load the Pandas libraries with alias 'pd'
import pandas as pd
import numpy as np

missingValues = []


def find_missing(data, size):
    arr = np.array(data)
    for i in range(1, size):
        if arr[i] != arr[i-1]+1:
            tempVal = arr[i-1]+1
            while tempVal != arr[i]:
                missingValues.append(tempVal)
                tempVal = tempVal+1


data = pd.read_csv("data-latest7thAug.csv")

data["gameNo"] = pd.to_numeric(
    data["gameNo"].str.split("#", n=1, expand=True)[1])

data.sort_values("gameNo", inplace=True)

duplicateDFRow = data[data.duplicated(subset=["gameNo"])]

data.drop_duplicates(subset=["gameNo"],
                     inplace=True)
size = len(data)
print("Total games: ", size)
find_missing(data["gameNo"], size)
print("Missing Values array: ", missingValues)

noOfMissings = len(missingValues)

if noOfMissings == 0:
    data.to_csv('dataCompletelatesttill7thAug.csv', mode='a', header=False)

print("Number of duplicates: ", len(duplicateDFRow))
print("Number of missings: ", noOfMissings)
