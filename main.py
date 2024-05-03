# main.py

import webscraper
import graphics

#Parte 1: Webscraping delle partite

#Ottiene i dati di login
USERNAME, PASSWORD = webscraper.login()

# Ottieni i dati delle partite
games_data = webscraper.scrape_games_data(USERNAME, PASSWORD)

#Salvo il mio dataframe su excel
print(games_data.head())
games_data.to_excel('output.xlsx', index=False)

#-------------------------------------------------------------------------------------------------------------------
#Parte 2: Elaborare i dati delle partite e pulizia dei dati

# Elabora i dati delle partite
webscraper.process_game_data(games_data, USERNAME)

#Pulizia del dataset
games_data_excel = webscraper.pulizia_dataset()

#-------------------------------------------------------------------------------------------------------------------

#Parte 3: Grafici

#Grafico rating ma con solo le partite da 10 minuti:

graphics.generate_chess_rating_rapid(games_data_excel)

#Grafico che mostra tutte le partite vinte, perse e pareggiate, visualizzabili tramite istogrammi

graphics.generate_chess_all_score(games_data_excel)

#Grafico che mostra le partite vinte, perse e pareggiate con ciascun colour tramite istogrammi

graphics.generate_chess_all_score_colour(games_data_excel)

#Grafico che mostra il winrate tra pezzi bianchi vs pezzi neri
graphics.generate_chess_winrate_colour(games_data_excel)

#Heatmap

graphics.generate_chess_heatmap(games_data_excel)

#Grafico "Quante mosse per colore pezzi in un game?"

graphics.generate_chess_plot_combined(games_data_excel)

#Grafico "Quante mosse per WinRate in un game?"

graphics.generate_chess_movesXwinrate(games_data_excel)

#Grafico "Time Pressure vs Wins"

graphics.generate_chess_timepressure(games_data_excel)
