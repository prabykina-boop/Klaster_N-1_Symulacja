from scipy.stats import weibull_min
import numpy as np

# --- PARAMETRY ROZKŁADU WEIBULLA (TTF - Czas do Awarii) ---

BETA = 2.0 # Parametr kształtu (ß): Wartość > 1 symuluje starzenie się i zużycie sprzętu
ETA = 500.0 # Parametr skali (η): Oznacza, że typowy czas życia serwera to 500 godzin
LOC = 0 # # Parametr położenia

def generate_server_ttf() :

    # Generuje Czas Do Awarii (TTF) dla pojedynczego serwera.

    ttf = weibull_min.rvs(c=BETA, scale=ETA, loc=LOC, size=1)[0]
    return max(0.01,ttf)