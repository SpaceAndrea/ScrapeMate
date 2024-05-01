# webscraper.py

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def login_chess_com(driver, username, password):
    LOGIN_URL = "https://www.chess.com/login"
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login"))).click()

def scrape_games_data(username, password):
    driver = setup_driver()
    login_chess_com(driver, username, password)
    time.sleep(5)  # Pause to ensure the page has loaded completely after login

    tables = []
    game_links = []
    GAMES_URL = "https://www.chess.com/games/archive?gameOwner=other_game&username=" + username + "&gameType=live&gameResult=&opponent=&opening=&color=&gameTourTeam=&timeSort=desc&rated=rated&startDate%5Bdate%5D=08%2F01%2F2013&endDate%5Bdate%5D=" + str(time.localtime().tm_mon) + "%2F" + str(time.localtime().tm_mday) + "%2F" + str(time.localtime().tm_year) + "&ratingFrom=&ratingTo=&page="

    try:
        for page_number in range(7):  # You can adjust the range based on the number of pages you expect
            driver.get(GAMES_URL + str(page_number + 1))
            time.sleep(5)
            # Extract tables and game links
            tables.append(pd.read_html(driver.page_source, attrs={'class': 'table-component table-hover archive-games-table'})[0])
            cells = driver.find_elements(By.CLASS_NAME, 'archive-games-user-cell')
            for cell in cells:
                link = cell.find_element(By.TAG_NAME, 'a').get_attribute('href')
                game_links.append(link)
    finally:
        driver.close()
        
    games = pd.concat(tables, ignore_index=True)
    games['Game Links'] = game_links
    return games

# Non aggiungere codice eseguibile al di fuori delle funzioni in questo file.
