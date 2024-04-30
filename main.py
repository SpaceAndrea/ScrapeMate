import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import requests
import csv
import datetime
import time
import hashlib
import os  
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
now = datetime.datetime.now()


USERNAME = "NightyBreeze"
PASSWORD = "SpringBreeze2001"
GAMES_URL = "https://www.chess.com/games/archive?gameOwner=other_game&username=" + \
        USERNAME + \
        "&gameType=live&gameResult=&opponent=&opening=&color=&gameTourTeam=&" + \
        "timeSort=desc&rated=rated&startDate%5Bdate%5D=08%2F01%2F2013&endDate%5Bdate%5D=" + \
        str(now.month) + "%2F" + str(now.day) + "%2F" + str(now.year) + \
        "&ratingFrom=&ratingTo=&page="
LOGIN_URL = "https://www.chess.com/login"

# Configurazione e avvio del webdriver
driver = webdriver.Chrome(options=options)
driver.get(LOGIN_URL)

# Attendi che l'elemento con ID 'username' sia presente nella pagina entro 10 secondi
username_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "username"))
)

# Inserisci l'username
username_input.send_keys(USERNAME)


# Attendi che l'elemento con ID 'password' sia presente nella pagina entro 10 secondi
password_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "password"))
)

# Inserisci la password
password_input.send_keys(PASSWORD)

# Attendi che l'elemento con ID 'login' sia presente nella pagina entro 10 secondi
login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "login"))
)

# Esegui il clic sul pulsante di login
login_button.click()

'''
# Attendi 5 secondi per il caricamento della pagina dopo il login
time.sleep(5)
'''

tables = []
game_links = []

for page_number in range(7):
    driver.get(GAMES_URL + str(page_number + 1))
    time.sleep(5)
    tables.append(
        pd.read_html(
            driver.page_source, 
            attrs={'class':'table-component table-hover archive-games-table'}
        )[0]
    )
    
    table_user_cells = driver.find_elements(By.CLASS_NAME, 'archive-games-user-cell')
    for cell in table_user_cells:
        link = cell.find_elements(By.TAG_NAME, 'a')[0]
        game_links.append(link.get_attribute('href'))
        
driver.close()

#Questo codice fa la stesse cose di quello sotto, ma dà poi errore: code unreachable
# games = pd.concat(tables)

#Inizializzo il dataframe vuoto
games = pd.DataFrame()

#Concateno i frame dei dati contenuti nella lista 'tables' nel dataframe 'games'
for table in tables:
    games = pd.concat([games, table], ignore_index=True)


identifier = pd.Series(
    games['Players'] + str(games['Result']) + str(games['Moves']) + games['Date']
).apply(lambda x: x.replace(" ", ""))

games.insert(   
    0, 
    'GameId', 
    identifier.apply(lambda x: hashlib.sha1(x.encode("utf-8")).hexdigest())
)

print(games.head(3))
games.to_excel('output.xlsx', index=False)

#PARTE 2 -------------------------------- GRAFICO

import re

# Definisci una funzione per estrarre i nomi dei giocatori, i rating bianchi e neri utilizzando espressioni regolari
def extract_player_info(players_string):
    match = re.findall(r'\b[A-Za-z0-9]+\b', players_string)
    ratings = re.findall(r'\((\d+)\)', players_string)
    return match[0], int(ratings[0]), match[2], int(ratings[1])

# Applica la funzione alla colonna 'Players' per estrarre i nomi dei giocatori, i rating bianchi e neri
games[['White Player', 'White Rating', 'Black Player', 'Black Rating']] = games['Players'].apply(lambda x: pd.Series(extract_player_info(x)))


'''
new = games.Players.str.split(" ", n=5, expand=True)
new = new.drop([1,4], axis=1)
new[2] = new[2].str.replace('(','').str.replace(')','').astype(int)
new[5] = new[5].str.replace('(','').str.replace(')','').astype(int)
new[0] = new[0].str.strip()  # Rimuovi gli spazi extra
new[3] = new[3].str.strip()  # Rimuovi gli spazi extra
games['White Player'] = new[0]
games['White Rating'] = new[2]
games['Black Player'] = games['Players'][3]
games['Black Rating'] = new[5]

print(new[0].iloc[0])
print(new[3].iloc[0])

print(new)
print(games['Players'])
'''
# Stampa le posizioni delle colonne nel DataFrame
for col_name in games.columns:
    col_position = games.columns.get_loc(col_name)
    print(f"Column '{col_name}' is at position: {col_position}")


#PUNTO DI CRISI:

# Add results
result = games.Result.str.split(" ", expand=True)
games['White Result'] = result[0]
games['Black Result'] = games['White Result'].apply(lambda x: 0 if x == '1' else (1 if x == '0' else '½'))
#games['Black Result'] = result[1]

# Drop unneccessary columns
games = games.rename(columns={"Unnamed: 0": "Time"})
games = games.drop(['Players', 'Unnamed: 6', 'Result', 'Accuracy'], axis=1)

print("Il nome con i pezzi bianchi è: ", games['White Player'] == USERNAME)
print("Il nome con i pezzi neri è: ", games['Black Player'] == USERNAME)

# Add calculated columns for wins, losses, draws, ratings, year, game links
conditions = [
        (games['White Player'] == USERNAME) & (games['White Result'] == '1'),
        (games['Black Player'] == USERNAME) & (games['Black Result'] == '1'),
        (games['White Player'] == USERNAME) & (games['White Result'] == '0'),
        (games['Black Player'] == USERNAME) & (games['Black Result'] == '0'),
        ]
choices = ["Win", "Win", "Loss", "Loss"]
games['W/L'] = np.select(conditions, choices, default="Draw")

conditions = [
        (games['White Player'] == USERNAME),
        (games['Black Player'] == USERNAME)
        ]
choices = ["White", "Black"]
games['Colour'] = np.select(conditions, choices)

conditions = [
        (games['White Player'] == USERNAME),
        (games['Black Player'] == USERNAME)
        ]
choices = [games['White Rating'], games['Black Rating']]
games['My Rating'] = np.select(conditions, choices)

conditions = [
        (games['White Player'] != USERNAME),
        (games['Black Player'] != USERNAME)
        ]
choices = [games['White Rating'], games['Black Rating']]
games['Opponent Rating'] = np.select(conditions, choices)

games['Rating Difference'] = games['Opponent Rating'] - games['My Rating']

print("I risultati delle partite sono: ",games[['White Result', 'Black Result']].head())

conditions = [
        (games['White Player'] == USERNAME) & (games['White Result'] == '1'),
        (games['Black Player'] == USERNAME) & (games['White Result'] == '0')
        #(games['Black Player'] == USERNAME) & (games['Black Result'] == '1')
        ]
choices = [1, 1]
games['Win'] = np.select(conditions, choices)

conditions = [
        (games['White Player'] == USERNAME) & (games['White Result'] == '0'),
        (games['Black Player'] == USERNAME) & (games['White Result'] == '1')
        #(games['Black Player'] == USERNAME) & (games['Black Result'] == '0')
        ]
choices = [1, 1]
games['Loss'] = np.select(conditions, choices)

conditions = [
        (games['White Player'] == USERNAME) & (games['White Result'] == '½'),
        (games['Black Player'] == USERNAME) & (games['White Result'] == '½')
        #(games['Black Player'] == USERNAME) & (games['Black Result'] == '½')
        ]
choices = [1, 1]
games['Draw'] = np.select(conditions, choices)

print("I risultati delle partite ORA sono: ",games[['White Result', 'Black Result']].head())

games['Year'] = pd.to_datetime(games['Date']).dt.to_period('Y')

games['Link'] = pd.Series(game_links)

# Optional calculated columns for indicating black or white pieces - uncomment if interested in these
games['Is_White'] = np.where(games['White Player']==USERNAME, 1, 0)
games['Is_Black'] = np.where(games['Black Player']==USERNAME, 1, 0)

# Correct date format
games["Date"] = pd.to_datetime(
    games["Date"].str.replace(",", "") + " 00:00", format = '%b %d %Y %H:%M'
)

print(games.head(3))
games.to_excel('output2.xlsx', index=False)


#Grafici
#Il primo grafico è possibilmente corretto, da rivedere se si riesce a fare con il codice iniziale della guida, altrimenti tenere questo.

#Ho messo la creazione del dataset pulito qua.
#La colonna 'W/L' contiene ancora errori invalidi.
games_excel = pd.read_excel('output2.xlsx')

#Filtro le partite non caricate correttamente (dovrebbero essere 21).
games_excel = games_excel[games_excel['Colour'] != '0']
games_excel = games_excel.dropna(subset=['Colour'])

games_excel.to_excel('output3.xlsx', index=False)

# Imposta lo stile dei grafici di seaborn
sns.set_style("dark")

# Converti la colonna "Data" in formato datetime
games_excel['Date'] = pd.to_datetime(games_excel['Date'], errors='coerce')

# Raggruppa per data e calcola la media di 'My Rating'
grouped_data = games_excel.groupby('Date')['My Rating'].mean().reset_index()

# crea una figura e un set di assi: 15 pollici in larghezza e 6 in lunghezza
fig, ax = plt.subplots(figsize=(15, 6))

# titolo del grafico
plt.title("Chess.com Rating Development", color="white") #da rimuovere il color

# Crea un grafico con gli elementi forniti: asse x = Data, asse y = rating
sns.lineplot(x="Date", y="My Rating", data=grouped_data, color="white")

# Imposta il colore degli assi e delle etichette
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.set_xlabel('Date', color='white')
ax.set_ylabel('My Rating', color='white')

# Imposta il colore dello sfondo della figura
fig.set_facecolor('black')
ax.set_facecolor("black")

# angolo di rotazione su 45 gradi per una migliore leggibilità
plt.xticks(rotation=45, color="white") #da rimuovere il color

# mostra il grafico
plt.show()
#Sono 320 partite ranked che però non variano dalla modalità del gioco.
#Considerare che le partite dalla 317 fino alla 32 sono state giocate nel 2021, quindi è plausibile che il grafico sia incentrato in quell'anno
# 2020: 3 partite
# 2021: 288 partite
# 2022: 3 partite
# 2023: 22 partite
# 2024: 4 partite
#Tot. 320 partite

#-------------------------------------------------------------------------------------------------------------------
#Stesso grafico ma con solo le partite da 10 minuti:

#Filtro le partite da 10 minuti

# Imposta lo stile dei grafici di seaborn
sns.set_style("dark")

games_excel_10min = games_excel[games_excel['Time'] == '10 min']
games_excel_10min.to_excel('10MinutesGames.xlsx', index=False)

# Raggruppa per data e calcola la media di 'My Rating'
grouped_data = games_excel_10min.groupby('Date')['My Rating'].mean().reset_index()

# crea una figura e un set di assi: 15 pollici in larghezza e 6 in lunghezza
fig, ax = plt.subplots(figsize=(15, 6))

# titolo del grafico
plt.title("Chess.com Rating Development in Rapid", color="white") #da rimuovere il color

# Crea un grafico con gli elementi forniti: asse x = Data, asse y = rating
sns.lineplot(x="Date", y="My Rating", data=grouped_data, color="blue")

# Imposta il colore degli assi e delle etichette
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.set_xlabel('Date', color='white')
ax.set_ylabel('My Rating', color='white')

# Imposta il colore dello sfondo della figura
fig.set_facecolor('black')
ax.set_facecolor("black")

# angolo di rotazione su 45 gradi per una migliore leggibilità
plt.xticks(rotation=45, color="white") #da rimuovere il color

# mostra il grafico
plt.show()

#--------------------------------------------------------------------------------------
#Grafico che mostra tutte le partite vinte, perse e pareggiate, visualizzabili tramite istogrammi

# Calcola il numero di partite vinte, perse e pareggiate
num_wins = games['Win'].sum()
num_losses = games['Loss'].sum()
num_draws = games['Draw'].sum()

#Imposto le dimensioni del grafico:
fig, ax = plt.subplots(figsize=(15,6))

# Crea un grafico a barre che mostra le Vittorie, Sconfitte e Pareggi
plt.bar(['Wins', 'Losses', 'Draws'], [num_wins, num_losses, num_draws], color=['green', 'red', 'blue'])
plt.xlabel('Result')
plt.ylabel('Number of Games')
plt.title('Number of Games by Result')
plt.show()

#----------------------------------------------------------------------------------------
#Grafico che mostra le partite vinte, perse e pareggiate con ciascun pezzo tramite istogrammi

# Raggruppa per colore e risultato, conta il numero di partite
grouped = games_excel.groupby(['Colour', 'White Result']).size().unstack(fill_value=0)

# Seleziona le righe in base al colore
white_games = games_excel[games_excel['Colour'] == 'White']
black_games = games_excel[games_excel['Colour'] == 'Black']

# Calcola il numero di vittorie, sconfitte e pareggi per i pezzi bianchi
num_wins_white = white_games['Win'].sum()
num_losses_white = white_games['Loss'].sum()
num_draws_white = white_games['Draw'].sum()

# Calcola il numero di vittorie, sconfitte e pareggi per i pezzi neri
num_wins_black = black_games['Win'].sum()
num_losses_black = black_games['Loss'].sum()
num_draws_black = black_games['Draw'].sum()

# Dati dei pezzi bianchi
white_results = [num_wins_white, num_losses_white, num_draws_white]

# Dati dei pezzi neri
black_results = [num_wins_black, num_losses_black, num_draws_black]

# Etichette per le barre
labels = ['Wins', 'Losses', 'Draws']

# Posizione delle barre
x = range(len(labels))

# Larghezza delle barre
width = 0.35

# Creazione del grafico a barre
fig, ax = plt.subplots()
bars_white = ax.bar([i - width/2 for i in x], white_results, width, label='White', color = '#E1D9D1', edgecolor = 'black')
bars_black = ax.bar([i + width/2 for i in x], black_results, width, label='Black', color = '#454545', edgecolor = 'black')

# Aggiunta delle etichette, del titolo e della legenda
ax.set_ylabel('Number of Games')
ax.set_title('Wins, Losses, and Draws by Colour')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Mostra il grafico
plt.show()

#--------------------------------------------------------------------------
#Grafico che mostra il winrate tra pezzi bianchi vs pezzi neri

# Calcola il numero totale di partite per i pezzi bianchi e neri
total_white_games = num_wins_white + num_losses_white + num_draws_white
total_black_games = num_wins_black + num_losses_black + num_draws_black

# Calcola il win rate per i pezzi bianchi e neri
win_rate_white = num_wins_white / total_white_games
win_rate_black = num_wins_black / total_black_games

# Dati dei win rate per i pezzi bianchi e neri
win_rates = [win_rate_white, win_rate_black]

# Etichette per le barre
labels = ['White', 'Black']

# Posizione delle barre
x = range(len(labels))

fig, ax = plt.subplots()
bars = ax.bar(x, win_rates, color=['#E1D9D1', '#454545'], edgecolor='black')

# Aggiunta delle etichette, del titolo e della legenda
ax.set_ylabel('Win Rate')
ax.set_title('Win Rate by Colour')
ax.set_xticks(x)
ax.set_xticklabels(labels)

# Mostra il grafico
plt.show()

#Praticamente questi due ultimi grafici fatti prendono di riferimento la lista di cui voglio vedere i dati sul grafico

#--------------------------------------------------------------------------------------------

#Heatmap? Non so quanto sia utile, da valutare

# Calcola la correlazione tra le colonne del DataFrame
corr = games_excel.corr()

# Crea la figura e l'asse per il grafico
fig, ax = plt.subplots(figsize=(14, 8))

# Crea la heatmap utilizzando seaborn
heatmap = sns.heatmap(corr, cmap="Greys", annot=True, fmt='.2f', linewidths=.05, ax=ax)

# Imposta il titolo del grafico
heatmap.set_title("Chess Results Correlation Heatmap")

# Aggiusta la posizione del titolo per essere più visibile
fig.subplots_adjust(top=0.93)

# Mostra il grafico
plt.show()
