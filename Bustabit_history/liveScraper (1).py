from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import json
import time
#import pytest
import pandas as pd
from datetime import datetime
from selenium.webdriver.chrome.options import DesiredCapabilities, Options

_url = "https://www.bustabit.com/game/"
urlPlay = "https://www.bustabit.com/play"
def getCurrentGameId(urlPlay):
    driver = webdriver.Safari()
    driver.get(urlPlay)
    wait = WebDriverWait(driver, 20)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    try:
        tr = soup.find('div', class_='table-responsive').table.tr
    except Exception as e:
        print(e)

    latestGameId = tr.find_all('td')[0]
    latestGameId = str(latestGameId.find('a', href=True)['href'])
    latestGameId = re.sub('/game/', '',latestGameId)
    driver.quit()
    return latestGameId



def getResults():

    lastPage = int(getCurrentGameId(urlPlay))  # 3450000
    currPage = lastPage - 20
    print(currPage)
    url = _url
    gameId = []
    bustNumber = []
    timeStamp = []
    count = 0
    driver = webdriver.Safari()
    while currPage <= lastPage:
        driver.get(url="{}{}".format(url, currPage))
        wait = WebDriverWait(driver, 20)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            div = soup.find('div', class_='col-sm-24 col-xs-24')
        except:
            time.sleep(2)
            driver.get(url="{}{}".format(url, currPage))
            wait = WebDriverWait(driver, 20)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'lxml')
            div = soup.find('div', class_='col-sm-24 col-xs-24')
        try:
            gameId.append(str(div.find('h4').get_text()))
        except:
            time.sleep(2)
            try:
                gameId.append(str(div.find('h4').get_text()))
            except:
                gameId.append('NAN')
        try:
            bustNumber.append(div.h5.find(
                'span', class_='bold').get_text())
        except:
            time.sleep(2)
            try:
                bustNumber.append(div.h5.find(
                    'span', class_='bold').get_text())
            except:
                bustNumber.append('NAN')
        try:
            timeStamp.append(div.find_all('h5')[1].get_text())
        except:
            time.sleep(2)
            try:
                timeStamp.append(div.find_all('h5')[1].get_text())
            except:
                timeStamp.append('NAN')
        currPage = currPage + 1

    driver.quit()
    saveResult(timeStamp, gameId, bustNumber)



def saveResult(timeStamp, gameId, bustNumber):
    dataTuples = list(zip(timeStamp, gameId, bustNumber))
    df = pd.DataFrame(dataTuples, columns=[
        'Time Stamp', 'GameID', 'Bust Number'])
    df.to_csv('data.csv', mode='a', header=False)


if __name__ == '__main__':
    getResults()
