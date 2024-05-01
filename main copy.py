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

# main.py

import webscraper

USERNAME = "NightyBreeze"
PASSWORD = "SpringBreeze2001"

# Ottieni i dati delle partite
games_data = webscraper.scrape_games_data(USERNAME, PASSWORD)

# Fai quello che ti serve con i dati, ad esempio salvarli o analizzarli
print(games_data.head())
games_data.to_excel('output.xlsx', index=False)


#PARTE 2 -------------------------------- GRAFICO

import re

# Definisci una funzione per estrarre i nomi dei giocatori, i rating bianchi e neri utilizzando espressioni regolari
def extract_player_info(players_string):
    match = re.findall(r'\b[A-Za-z0-9]+\b', players_string)
    ratings = re.findall(r'\((\d+)\)', players_string)
    return match[0], int(ratings[0]), match[2], int(ratings[1])

# Applica la funzione alla colonna 'Players' per estrarre i nomi dei giocatori, i rating bianchi e neri
games_data[['White Player', 'White Rating', 'Black Player', 'Black Rating']] = games_data['Players'].apply(lambda x: pd.Series(extract_player_info(x)))

# Stampa le posizioni delle colonne nel DataFrame
for col_name in games_data.columns:
    col_position = games_data.columns.get_loc(col_name)
    print(f"Column '{col_name}' is at position: {col_position}")


#PUNTO DI CRISI:

# Add results
result = games_data.Result.str.split(" ", expand=True)
games_data['White Result'] = result[0]
games_data['Black Result'] = games_data['White Result'].apply(lambda x: 0 if x == '1' else (1 if x == '0' else '½'))
#games_data['Black Result'] = result[1]

# Drop unneccessary columns
games_data = games_data.rename(columns={"Unnamed: 0": "Time"})
games_data = games_data.drop(['Players', 'Unnamed: 6', 'Result', 'Accuracy'], axis=1)

print("Il nome con i pezzi bianchi è: ", games_data['White Player'] == USERNAME)
print("Il nome con i pezzi neri è: ", games_data['Black Player'] == USERNAME)

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

print("I risultati delle partite sono: ",games_data[['White Result', 'Black Result']].head())

conditions = [
        (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '1'),
        (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '0')
        #(games_data['Black Player'] == USERNAME) & (games_data['Black Result'] == '1')
        ]
choices = [1, 1]
games_data['Win'] = np.select(conditions, choices)

conditions = [
        (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '0'),
        (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '1')
        #(games_data['Black Player'] == USERNAME) & (games_data['Black Result'] == '0')
        ]
choices = [1, 1]
games_data['Loss'] = np.select(conditions, choices)

conditions = [
        (games_data['White Player'] == USERNAME) & (games_data['White Result'] == '½'),
        (games_data['Black Player'] == USERNAME) & (games_data['White Result'] == '½')
        #(games_data['Black Player'] == USERNAME) & (games_data['Black Result'] == '½')
        ]
choices = [1, 1]
games_data['Draw'] = np.select(conditions, choices)

print("I risultati delle partite ORA sono: ",games_data[['White Result', 'Black Result']].head())

games_data['Year'] = pd.to_datetime(games_data['Date']).dt.to_period('Y')

games_data['Link'] = pd.Series(games_data['Game Links'])

# Optional calculated columns for indicating black or white pieces - uncomment if interested in these
games_data['Is_White'] = np.where(games_data['White Player']==USERNAME, 1, 0)
games_data['Is_Black'] = np.where(games_data['Black Player']==USERNAME, 1, 0)

# Correct date format
games_data["Date"] = pd.to_datetime(
    games_data["Date"].str.replace(",", "") + " 00:00", format = '%b %d %Y %H:%M'
)

print(games_data.head(3))
games_data.to_excel('output2.xlsx', index=False)


#Grafici
#Il primo grafico è possibilmente corretto, da rivedere se si riesce a fare con il codice iniziale della guida, altrimenti tenere questo.

#Ho messo la creazione del dataset pulito qua.
games_data_excel = pd.read_excel('output2.xlsx')

#Filtro le partite non caricate correttamente (dovrebbero essere 21).
games_data_excel = games_data_excel[games_data_excel['Colour'] != '0']
games_data_excel = games_data_excel.dropna(subset=['Colour'])

games_data_excel.to_excel('output3.xlsx', index=False)

# Imposta lo stile dei grafici di seaborn
sns.set_style("dark")

# Converti la colonna "Data" in formato datetime
games_data_excel['Date'] = pd.to_datetime(games_data_excel['Date'], errors='coerce')

# Raggruppa per data e calcola la media di 'My Rating'
grouped_data = games_data_excel.groupby('Date')['My Rating'].mean().reset_index()

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
plt.savefig("TotalRating.png")
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

games_data_excel_10min = games_data_excel[games_data_excel['Time'] == '10 min']
games_data_excel_10min.to_excel('10Minutesgames_data.xlsx', index=False)

# Raggruppa per data e calcola la media di 'My Rating'
grouped_data = games_data_excel_10min.groupby('Date')['My Rating'].mean().reset_index()

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
plt.savefig("RapidRating.png")

#--------------------------------------------------------------------------------------
#Grafico che mostra tutte le partite vinte, perse e pareggiate, visualizzabili tramite istogrammi

# Calcola il numero di partite vinte, perse e pareggiate
num_wins = games_data['Win'].sum()
num_losses = games_data['Loss'].sum()
num_draws = games_data['Draw'].sum()

#Imposto le dimensioni del grafico:
fig, ax = plt.subplots(figsize=(15,6))

# Crea un grafico a barre che mostra le Vittorie, Sconfitte e Pareggi
plt.bar(['Wins', 'Losses', 'Draws'], [num_wins, num_losses, num_draws], color=['#E1D9D1', '#454545', 'grey'], edgecolor='black')
plt.xlabel('Result')
plt.ylabel('Number of games_data')
plt.title('Number of games_data by Result')
plt.savefig("AllScore.png")

#----------------------------------------------------------------------------------------
#Grafico che mostra le partite vinte, perse e pareggiate con ciascun pezzo tramite istogrammi

# Raggruppa per colore e risultato, conta il numero di partite
grouped = games_data_excel.groupby(['Colour', 'White Result']).size().unstack(fill_value=0)

# Seleziona le righe in base al colore
white_games_data = games_data_excel[games_data_excel['Colour'] == 'White']
black_games_data = games_data_excel[games_data_excel['Colour'] == 'Black']

# Calcola il numero di vittorie, sconfitte e pareggi per i pezzi bianchi
num_wins_white = white_games_data['Win'].sum()
num_losses_white = white_games_data['Loss'].sum()
num_draws_white = white_games_data['Draw'].sum()

# Calcola il numero di vittorie, sconfitte e pareggi per i pezzi neri
num_wins_black = black_games_data['Win'].sum()
num_losses_black = black_games_data['Loss'].sum()
num_draws_black = black_games_data['Draw'].sum()

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
ax.set_ylabel('Number of games_data')
ax.set_title('Wins, Losses, and Draws by Colour')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Mostra il grafico
plt.savefig("AllScoreColour.png")

#--------------------------------------------------------------------------
#Grafico che mostra il winrate tra pezzi bianchi vs pezzi neri

# Calcola il numero totale di partite per i pezzi bianchi e neri
total_white_games_data = num_wins_white + num_losses_white + num_draws_white
total_black_games_data = num_wins_black + num_losses_black + num_draws_black

# Calcola il win rate per i pezzi bianchi e neri
win_rate_white = num_wins_white / total_white_games_data
win_rate_black = num_wins_black / total_black_games_data

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
plt.savefig("WinRate.png")

#Praticamente questi due ultimi grafici fatti prendono di riferimento la lista di cui voglio vedere i dati sul grafico

#--------------------------------------------------------------------------------------------
#Heatmap? Non so quanto sia utile, da valutare

# Seleziona solo colonne numeriche
games_data_numeric = games_data_excel.select_dtypes(include=[np.number])

# Calcola la correlazione tra le colonne del DataFrame
corr = games_data_numeric.corr()

# Crea la figura e l'asse per il grafico
fig, ax = plt.subplots(figsize=(14, 8))

# Crea la heatmap utilizzando seaborn
heatmap = sns.heatmap(corr, cmap="Greys", annot=True, fmt='.2f', linewidths=.05, ax=ax)

# Imposta il titolo del grafico
heatmap.set_title("Chess Results Correlation Heatmap")

# Aggiusta la posizione del titolo per essere più visibile
fig.subplots_adjust(top=0.93)

# Mostra il grafico
plt.savefig("HeatMap.png")

#--------------------------------------------------------------------------------------------
#Grafico "Quante mosse per colore pezzi in un game?"

fig = plt.figure(figsize=(20, 8))  # Definisci la dimensione della figura

# Aggiungi il primo subplot nella prima posizione di una griglia 1x2
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_title("Distribuzione del numero di mosse")  # Imposta il titolo del primo grafico
sns.histplot(games_data_excel, x="Moves", hue="Colour", palette={"Black": "Black", "White": "Grey"}, ax=ax1)
ax1.set_xlabel("Numero di mosse")  # Etichetta per l'asse x
ax1.set_ylabel("Frequenza")  # Etichetta per l'asse y

# Aggiungi il secondo subplot nella seconda posizione della stessa griglia 1x2
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_title("Densità del numero di mosse")  # Imposta il titolo del secondo grafico
sns.kdeplot(data=games_data_excel, x="Moves", hue="Colour", palette={"Black": "Black", "White": "Grey"}, ax=ax2, fill=True)
ax2.set_xlabel("Numero di mosse")  # Etichetta per l'asse x
ax2.set_ylabel("Densità")  # Etichetta per l'asse y
ax2.set_xlim(0, None)  # Imposta il limite inferiore dell'asse x a 0
fig.suptitle("How many moves in my typical game?")  # Imposta il titolo della figura
plt.savefig("CombinedChessPlots.png")  # Salva la figura intera con entrambi i grafici

#---------------------------------------------------------------------------------------------
#Grafico "Quante mosse per WinRate in un game?"

# # Aggiungi una colonna 'count' che è sempre 1 per facilitare l'aggregazione
# games_data_excel['count'] = 1

# # Aggrega per numero di mosse, calcolando il numero totale di partite e vittorie per ogni numero di mosse
# win_rate_data = games_data_excel.groupby('Moves').agg(total_games_data=('count', 'sum'),
#                                                  wins=('Win', 'sum')).reset_index()

# # Calcola la percentuale di vittorie
# win_rate_data['win_rate'] = win_rate_data['wins'] / win_rate_data['total_games_data'] * 100

# # Creazione del grafico
# plt.figure(figsize=(14, 8))
# sns.lineplot(data=win_rate_data, x='Moves', y='win_rate')
# plt.title("Does the amount of moves affect my win rate?")
# plt.xlabel("Number of Moves")
# plt.ylabel("Win Rate (%)")
# plt.grid(True)
# plt.savefig("Moves_VS_WinRate.png")

fig = plt.figure(figsize=(14,8))
ax = fig.add_subplot(1,1,1)
ax.set_title("Does the amount of moves affect my win rate?")

sns.histplot(games_data_excel, x="Moves", hue="W/L", multiple="stack", palette={"Loss": "Black", "Win": "Gray", "Draw": "lightgray"})
plt.savefig("Moves_VS_WinRate.png")

#---------------------------------------------------------------------------------------------
#Grafico "Time Pressure vs Wins"

fig = plt.figure(figsize=(14,8))
plt.title("How is time pressure affecting my game?")
sns.countplot(data=games_data_excel, x='Time', hue="W/L", palette={"Win":"#CCCCCC", "Loss":"Grey", "Draw":"White"}, edgecolor="Black");
plt.savefig("TimePressure.png")