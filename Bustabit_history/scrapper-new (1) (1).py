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


def getResults():
    currPage = 2701225
    lastPage = 2710876  # 3450000
    # options = webdriver.ChromeOptions()
    # # options.add_argument('maximize')
    # options.add_argument("--profile-directory=Default")
    # options.add_argument(
    #     "--user-data-dir=~/home/faraz/.config/google-chrome")
    # print(options.arguments)
    chrome_options = Options()
    chrome_options.add_argument(
        "user-data-dir=/home/faraz/devhike/devhikesolutions-bustabitrepo-488ae69a0e25/chrome_profiles")  # change to profile path
    chrome_options.add_argument('profile-directory=Profile_1')
    # chrome_options.add_extension(
    #     extension='extension_3_27_6_0.crx')

    # chrome_options.add_argument("--enable-extensions")

    # driver = webdriver.Chrome(
    #     options=chrome_options, executable_path="/usr/local/bin/chromedriver")

    # options.addArguments("load-extension=/path/to/extension")
    # ChromeDriver driver = new ChromeDriver(options)

    url = _url
    gameId = []
    bustNumber = []
    timeStamp = []
    count = 0
    maxLimit = 50
    while currPage <= lastPage:
        driver = webdriver.Chrome(
            options=chrome_options, executable_path="/usr/local/bin/chromedriver")
        while count < maxLimit:
            count += 1
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
        count = 0
        saveResult(timeStamp, gameId, bustNumber)
        gameId = []
        bustNumber = []
        timeStamp = []


def saveResult(timeStamp, gameId, bustNumber):
    dataTuples = list(zip(timeStamp, gameId, bustNumber))
    df = pd.DataFrame(dataTuples, columns=[
        'Time Stamp', 'GameID', 'Bust Number'])
    df.to_csv('data.csv', mode='a', header=False)


if __name__ == '__main__':
    getResults()
