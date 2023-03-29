import numpy as np
import pickle
# import file
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from typing import Optional
import joblib
import pandas as pd
import os
import traceback
import jsonify
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import json
import time
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from selenium.webdriver.chrome.options import DesiredCapabilities, Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Scrapper code...............
_url = "https://www.bustabit.com/game/"
urlPlay = "https://www.bustabit.com/play"


class CurrentGameRequest(BaseModel):
    latestGameNumber: str
    predictionBustNumbers: list


def getCurrentGameId(urlPlay):
    # chrome_options.add_argument("--headless")

    print("bbbbbbbbbbbbbbb")
    chrome_options = Options()
    chrome_options.add_argument(
        "user-data-dir=/home/faraz/devhike/devhikesolutions-bustabitrepo-488ae69a0e25/fastapp/chrome_profiles")  # change to profile path
    chrome_options.add_argument('profile-directory=Profile_1')
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        options=chrome_options, executable_path="/usr/local/bin/chromedriver")

    driver.get(urlPlay)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    err = soup.find('span', class_='cf-error-type')
    if err:
        print(err)

    # print(soup)
    # try:
    tr = soup.find('div', class_='table-responsive').table.tr
    # except Exception as e:
    #     print(e)
    # print(tr)
    latestGameId = tr.find_all('td')[0]
    latestGameId = str(latestGameId.find('a', href=True)['href'])
    latestGameId = re.sub('/game/', '', latestGameId)
    driver.quit()
    print("current page number(latest): ", latestGameId)
    return latestGameId

# gives current game ids bust number only

#########################################


@app.post("/latestGameRetry")
def getCurrentResultRetry(currentGameRequest: CurrentGameRequest):
    print("aaaaaaaaa")
    chrome_options = Options()
    chrome_options.add_argument(
        "user-data-dir=/home/faraz/devhike/devhikesolutions-bustabitrepo-488ae69a0e25/fastapp/chrome_profiles")  # change to profile path
    chrome_options.add_argument('profile-directory=Profile_1')
    # chrome_options.add_argument("--headless")
    # currPage = int(getCurrentGameId(urlPlay))
    # print("current page number(latest): ", currPage)
    gameId = []
    bustNumber = []
    timeStamp = []
    driver = webdriver.Chrome(
        options=chrome_options, executable_path="/usr/local/bin/chromedriver")
    latestGameId = currentGameRequest.latestGameNumber

    predictionNumbers = []
    predictionNumbers = currentGameRequest.predictionBustNumbers

    url = urlPlay
    while latestGameId == currentGameRequest.latestGameNumber:
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        # time.sleep(3)
        el = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id=\"root\"]/div/div/div[4]/div[3]/div/table/tbody/tr/td[1]/a")))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            tr = soup.find('div', class_='table-responsive').table.tr
        except Exception as e:
            print(e)
        temp = tr.find_all('td')[0]
        latestBustNumber = str(temp.find('a').get_text())
        latestGameId = str(temp.find('a', href=True)['href'])
        latestGameId = re.sub('/game/', '', latestGameId)
        # print(latestBustNumber)
        # print(latestGameId)
        time.sleep(1)

    [i.strip() for i in bustNumber]
    predictionNumbers.append(latestBustNumber)
    predicted_value = realTimePredictor(
        predictionNumbers[-16:], "mySavedDict.txt")
    print("predicted value: ", predicted_value)

    driver.quit()
    return ({"gameId": latestGameId, "bustNumber": latestBustNumber, "predictionResult": predicted_value})
########################################


@app.post("/beforeGame")
def getResultsBefore(request: Request):
    chrome_options = Options()
    chrome_options.add_argument(
        "user-data-dir=/home/faraz/devhike/devhikesolutions-bustabitrepo-488ae69a0e25/fastapp/chrome_profiles")  # change to profile path
    chrome_options.add_argument('profile-directory=Profile_1')
    driver = webdriver.Chrome(
        options=chrome_options, executable_path="/usr/local/bin/chromedriver")

    # wait = WebDriverWait(driver, 20)
    # time.sleep(5)
    url = urlPlay
    gameNumber = []
    bustNumber = []
    driver.get(url)
    time.sleep(3)
    wait = WebDriverWait(driver, 40)

    el = WebDriverWait(driver, 30).until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div/div/div/div[6]/div/div[1]/ul/li[2]/a")))
    button = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[6]/div/div[1]/ul/li[2]/a").click()

    print("found history")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        div = soup.find(
            'div', class_='_2ivuyERPS12JSJ5IG8kEVf')
    except:
        print("couldn't load history")
    try:
        tbody = div.find('tbody')
        i = tbody.find_all('tr')
        for j in range(16, -1, -1):
            td = i[j].find('td')
            tempGame = str(td.find('a', href=True)['href'])
            tempGame = re.sub('/game/', '', tempGame)
            temp = td.find('a').get_text()
            temp = str(temp)
            print(tempGame)
            gameNumber.append(tempGame)
            bustNumber.append(temp)
        print(bustNumber)
    except:
        print("couldn't process your request")
    driver.quit()

    # saveResult(timeStamp, gameId, bustNumber)
    print("befores game", gameNumber)

    print("befores bust", bustNumber)

    # print(results['bustNumber'][-16:])
    [i.strip() for i in bustNumber]

    predicted_value = realTimePredictor(
        bustNumber[:16], "mySavedDict.txt")
    print("predicted value: ", predicted_value)

    return({"bustNumber": bustNumber[:16], "gameNumber": gameNumber[:16], "predictionResult": predicted_value})


def saveResult(timeStamp, gameId, bustNumber):
    dataTuples = list(zip(timeStamp, gameId, bustNumber))
    df = pd.DataFrame(dataTuples, columns=[
        'Time Stamp', 'GameID', 'Bust Number'])
    # df.to_csv('data.csv', mode='a', header=False)
    print(df)


# if __name__ == '__main__':
#     getCurrentResult()
# End................................


def labels(value):
    if value < 2:
        return 0
    else:
        return 1


def preprocess(value):
    return float(value[:-1].replace(',', ''))


def realTimePredictor(series, path):
    series = list(map(preprocess, series))
    series = map(labels, series)
    series = np.array(list(series))
    with open(path, "rb") as myFile:
        Model = pickle.load(myFile)
    listToStr = ''.join(map(str, series))
    Str0 = listToStr+"0"
    Str1 = listToStr+"1"
    Str0_1 = [Model[Str0], Model[Str1]]
    print(Str0_1)
    maxval = max(Str0_1)
    if maxval == Model[Str0]:
        return 0  # default is to predict zero
    else:
        return 1


@ app.get("/")
def home(request: Request):

    return templates.TemplateResponse("home.html", {"request": request})
