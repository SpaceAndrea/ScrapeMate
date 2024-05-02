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
import graphics

USERNAME = "NightyBreeze"
PASSWORD = "SpringBreeze2001"

'''
# Ottieni i dati delle partite
games_data = webscraper.scrape_games_data(USERNAME, PASSWORD)

# Fai quello che ti serve con i dati, ad esempio salvarli o analizzarli
print(games_data.head())
games_data.to_excel('output.xlsx', index=False)

#Parte 2: Elaborare i dati delle partite e pulizia dei dati
# Elabora i dati delle partite
webscraper.process_game_data(games_data, USERNAME)
'''
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
#---------------------------------------------------------------------------------------------
#Grafico "Time Pressure vs Wins"

graphics.generate_chess_timepressure(games_data_excel)