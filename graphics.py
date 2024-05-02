# graphics.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#Sono 320 partite ranked che però non variano dalla modalità del gioco.
#Considerare che le partite dalla 317 fino alla 32 sono state giocate nel 2021, quindi è plausibile che il grafico sia incentrato in quell'anno
# 2020: 3 partite
# 2021: 288 partite
# 2022: 3 partite
# 2023: 22 partite
# 2024: 4 partite
#Tot. 320 partite

def generate_chess_rating_plot(data):
    # Imposta lo stile dei grafici di seaborn
    sns.set_style("dark")

    # Converti la colonna "Data" in formato datetime
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # Raggruppa per data e calcola la media di 'My Rating'
    grouped_data = data.groupby('Date')['My Rating'].mean().reset_index()

    # crea una figura e un set di assi: 15 pollici in larghezza e 6 in lunghezza
    fig, ax = plt.subplots(figsize=(15, 6))

    # titolo del grafico
    plt.title("Chess.com Rating Development", color="white") 

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
    plt.xticks(rotation=45, color="white")

    #mostra il grafico
    plt.show()

    # salva il grafico
    plt.savefig("TotalRating.png")

    # Chiudi la figura per liberare la memoria
    plt.close()

def generate_chess_rating_rapid(games_data_excel):
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

def generate_chess_all_score(games_data_excel):
    fig, ax = plt.subplots(figsize=(15,6))
    #oppure
    #plt.figure(figsize=(15,6))
    plt.title("Wins, Losses and Draws")
    plt.xlabel('Result')
    plt.ylabel('Number of games')
    sns.countplot(data=games_data_excel, x='W/L', palette={"Win": "#E1D9D1", "Loss": "#454545", "Draw": "grey"}, edgecolor="black")
    plt.savefig("AllScore2.png")

def generate_chess_all_score_colour(games_data_excel):
    fig, ax = plt.subplots(figsize=(8,6))
    plt.title("Wins, Losses and Draws by Colour")
    plt.xlabel(None)
    plt.ylabel('Number of games')
    sns.countplot(data=games_data_excel, x='W/L', hue="Colour", palette={"Black": "#454545", "White": "#E1D9D1"}, edgecolor="black");
    plt.savefig("AllScoreColour2.png")


def generate_chess_winrate_colour(games_data_excel):
    fig, ax = plt.subplots(figsize=(8,6))
    # ax.set_title("Win Rate by Colour")
    plt.title("Win Rate by Colour")
    sns.barplot(data=games_data_excel, x='Colour', y='Win', palette={"Black": "#454545", "White": "#E1D9D1"}, edgecolor="black", errorbar="ci");
    #errorbar="ci" è l'intervallo di confidenza
    plt.savefig("WinRate2.png")

def generate_chess_heatmap(games_data_excel):
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
    plt.savefig("HeatMap2.png")

def generate_chess_plot_combined(games_data_excel):
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
    plt.savefig("CombinedChessPlots2.png")  # Salva la figura intera con entrambi i grafici

def generate_chess_movesXwinrate(games_data_excel):
    fig = plt.figure(figsize=(14,8))
    ax = fig.add_subplot(1,1,1)
    ax.set_title("Does the amount of moves affect my win rate?")

    sns.histplot(games_data_excel, x="Moves", hue="W/L", multiple="stack", palette={"Loss": "Black", "Win": "Grey", "Draw": "lightgray"})
    plt.savefig("Moves_VS_WinRate2.png")


def generate_chess_timepressure(games_data_excel):
    fig = plt.figure(figsize=(14,8))
    plt.title("How is time pressure affecting my game?")
    sns.countplot(data=games_data_excel, x='Time', hue="W/L", palette={"Win":"Grey", "Loss":"Black", "Draw":"White"}, edgecolor="Black");
    plt.savefig("TimePressure.png")