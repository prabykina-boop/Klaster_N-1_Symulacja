from weibull_model import generate_server_ttf
from ttr_model import generate_corrective_ttr

class Server:

    def __init__(self, server_id, initial_state="UP"):
        self.id = server_id
        self.state = initial_state
        # Czas pozostały do awarii
        self.ttf_remaining = 0.0
        # Czas pozostały do końca naprawy
        self.ttr_duration = 0.0
        # Czas, w którym serwer uległ awarii
        self.fail_time = None

        # Jeśli serwer startuje w stanie innym niż DOWN, generuje pierwszy TTF
        if self.state != "DOWN":
            self.start_life()

    def start_life(self):
        # Generuje nowy, losowy czas do następnej awarii
        self.ttf_remaining = generate_server_ttf()

        self.state = "UP"
        self.ttr_duration = 0.0

    # AWARIA (PRZEJŚCIE DO STANU DOWN)
    def fail(self):
        self.state = "DOWN"
        # Generuje czas trwania naprawy
        self.ttr_duration = generate_corrective_ttr()
        # Zeruje pozostały czas TTF
        self.ttf_remaining = 0.0

    # AKTYWACJA (z STANDBY na UP)
    def activate(self):
        # Przełącza stan na aktywny (UP)
        if self.state == "STANDBY":
            self.state = "UP"

    # PRZEJŚCIE DO STANU STANDBY
    def standby(self):
        # Przełącza stan na zapasowy
        if self.state == "UP":
            self.state = "STANDBY"