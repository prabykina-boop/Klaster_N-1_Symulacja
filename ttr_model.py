import numpy as np

# --- PARAMETRY CZASU NAPRAWY (TTR) W TRYBIE KOREKCYJNYM ---

TTR_CORRECTIVE_MEAN = 4.0 # Średni czas naprawy awaryjnej (np. 4 godziny)
TTR_CORRECTIVE_STD = 1.5 # Odchylenie standardowe (duża niepewność, bo to awaria)

def generate_corrective_ttr():
    # Generuje Czas Naprawy
    ttr = np.random.normal(TTR_CORRECTIVE_MEAN, TTR_CORRECTIVE_STD)
    return max(0.1,ttr)

if __name__ == '__main__':
    print('--- TTR Module Test ---')
    print(f"Random Corrective TTR: {generate_corrective_ttr():.2f} hours")