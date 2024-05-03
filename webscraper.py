# webscraper.py

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import numpy as np

#Questa funzione restituisce i parametri di login
def login():
    # Chiedi all'utente di inserire username e password
    username_input = input("Inserisci il tuo username: ")
    password_input = input("Inserisci la tua password: ")

    print("Accesso consentito. Benvenuto!")
    return username_input, password_input

#Questa funzione configura e avvia il browser automatizzato
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

#Questa funzione gestisce il processo di login su chess.com
def login_chess_com(driver, username, password):
    LOGIN_URL = "https://www.chess.com/login"
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login"))).click()

#Questa è la funzione principale che applica il processo di scraping
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
        driver.close() #assicura che il driver si chiuda correttamente dopo lo scraping, anche in caso di errori.
        
    games = pd.concat(tables, ignore_index=True)
    games['Game Links'] = game_links
    return games

#Questa funzione estrae le informazioni dei giocatori -- libreria 're' (regex) per estrarre i nomi dei giocatori e punteggi
def extract_player_info(players_string):
    match = re.findall(r'\b[A-Za-z0-9]+\b', players_string) #occorrenze sequenze alfanumeriche, cattura i nomi dei giocatori
    ratings = re.findall(r'\((\d+)\)', players_string) #occorrenze numeri tra parantesi, cattura i punteggi dei giocatori
    return match[0], int(ratings[0]), match[2], int(ratings[1]) #tupla contente nome e risultato dei giocatori

#Questa funzione elabora i dati delle partite presenti nel dataframe per un utente specifico (USERNAME)
def process_game_data(games_data, USERNAME):
    games_data[['White Player', 'White Rating', 'Black Player', 'Black Rating']] = games_data['Players'].apply(lambda x: pd.Series(extract_player_info(x)))
    # Add results
    result = games_data.Result.str.split(" ", expand=True)
    games_data['White Result'] = result[0]
    games_data['Black Result'] = games_data['White Result'].apply(lambda x: 0 if x == '1' else (1 if x == '0' else '½'))
    # Drop unneccessary columns
    games_data = games_data.rename(columns={"Unnamed: 0": "Time"})
    games_data = games_data.drop(['Players', 'Unnamed: 6', 'Result', 'Accuracy'], axis=1)
    # Add calculated columns for wins, losses, draws, ratings, year, game links
    conditions = [
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '1'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '0'),
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '0'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '1'),
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '½'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '½'),
            ]
    choices = ["Win", "Win", "Loss", "Loss", "Draw", "Draw"]
    games_data['W/L'] = np.select(conditions, choices)
    conditions = [
            (games_data['White Player'] == USERNAME),
            (games_data['Black Player'] == USERNAME)
            ]
    choices = ["White", "Black"]
    games_data['Colour'] = np.select(conditions, choices)
    conditions = [
            (games_data['White Player'] == USERNAME),
            (games_data['Black Player'] == USERNAME)
            ]
    choices = [games_data['White Rating'], games_data['Black Rating']]
    games_data['My Rating'] = np.select(conditions, choices)
    conditions = [
            (games_data['White Player'] != USERNAME),
            (games_data['Black Player'] != USERNAME)
            ]
    choices = [games_data['White Rating'], games_data['Black Rating']]
    games_data['Opponent Rating'] = np.select(conditions, choices)
    games_data['Rating Difference'] = games_data['Opponent Rating'] - games_data['My Rating']
    conditions = [
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '1'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '0')
            ]
    choices = [1, 1]
    games_data['Win'] = np.select(conditions, choices)
    conditions = [
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '0'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '1')
            ]
    choices = [1, 1]
    games_data['Loss'] = np.select(conditions, choices)
    conditions = [
            (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '½'),
            (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '½')
            ]
    choices = [1, 1]
    games_data['Draw'] = np.select(conditions, choices)
    games_data['Year'] = pd.to_datetime(games_data['Date']).dt.to_period('Y')
    games_data['Link'] = pd.Series(games_data['Game Links'])
    # Optional calculated columns for indicating black or white pieces - uncomment if interested in these
    # games_data['Is_White'] = np.where(games_data['White Player']==USERNAME, 1, 0)
    # games_data['Is_Black'] = np.where(games_data['Black Player']==USERNAME, 1, 0)
    # Correct date format
    games_data["Date"] = pd.to_datetime(
        games_data["Date"].str.replace(",", "") + " 00:00", format = '%b %d %Y %H:%M'
    )
    print(games_data.head(3))
    games_data.to_excel('output2.xlsx', index=False)

#Questa funzione pulisce il dataset
def pulizia_dataset():
#Ho messo la creazione del dataset pulito qua.
    games_data_excel = pd.read_excel('output2.xlsx')

#Filtro le partite non caricate correttamente (dovrebbero essere 21).
    games_data_excel = games_data_excel[games_data_excel['Colour'] != '0']
    games_data_excel = games_data_excel.dropna(subset=['Colour'])

    games_data_excel.to_excel('output3.xlsx', index=False)

    return games_data_excel
