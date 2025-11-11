from server import Server

SIM_DURATION = 8760.0

class Base_Model_Engine:

    def __init__(self):
        self.current_time = 0.0
        # Inicjalizuje 3 serwery
        self.servers = [Server(i) for i in range(1, 4)]

        self.state_durations = {'S3': 0.0, 'S2': 0.0, 'S1': 0.0, 'S0': 0.0}
        self.num_failures = 0

        # Zmienne do śledzenia napraw
        self.total_repair_time = 0.0
        self.repair_count = 0
        # Lista do rejestrowania momentów awarii systemu
        self.failure_timestamps = []

    def get_cluster_state(self):
        # Liczy serwery, które nie są w stanie "DOWN"
        num_available = sum(1 for s in self.servers if s.state != "DOWN")

        # Określenie stanu
        if num_available == 3: return 'S3'
        if num_available == 2: return 'S2'
        if num_available == 1: return 'S1'
        return 'S0'

    def update_state_duration(self, state, duration):
        if duration > 0:
            self.state_durations[state] += duration

    def run_simulation(self):
        current_cluster_state = self.get_cluster_state()

        while self.current_time < SIM_DURATION:

            next_event_time = SIM_DURATION - self.current_time
            event_type = None
            responsible_server = None

            # Najkrótszy czas do następnej awarii lub końca naprawy)
            for s in self.servers:
                # Sprawdza czas do awarii
                if s.state == "UP" and s.ttf_remaining > 0 and s.ttf_remaining < next_event_time:
                    next_event_time = s.ttf_remaining
                    event_type = "FAILURE"
                    responsible_server = s
                # Sprawdza czas do końca naprawy
                elif s.state == "DOWN" and s.ttr_duration > 0 and s.ttr_duration < next_event_time:
                    next_event_time = s.ttr_duration
                    event_type = "REPAIR_END"
                    responsible_server = s

            if self.current_time + next_event_time >= SIM_DURATION:
                # Dodaje pozostały czas do aktualnego stanu i kończy pętlę
                self.update_state_duration(current_cluster_state, SIM_DURATION - self.current_time)
                self.current_time = SIM_DURATION
                break

            self.update_state_duration(current_cluster_state, next_event_time)
            self.current_time += next_event_time

            # Zmniejsza pozostały TTF lub TTR o czas, który upłynął
            for s in self.servers:
                if s.state == "UP":
                    s.ttf_remaining = max(0.0, s.ttf_remaining - next_event_time)
                elif s.state == "DOWN":
                    s.ttr_duration = max(0.0, s.ttr_duration - next_event_time)

            # Przejście stanu
            if event_type == "FAILURE":
                # Serwer się psuje, rejestruje czas awarii i zwiększa licznik awarii
                responsible_server.fail()
                responsible_server.fail_time = self.current_time
                self.num_failures += 1
                self.failure_timestamps.append(self.current_time)

            elif event_type == "REPAIR_END":
                # Serwer zostaje naprawiony, aktualizuje statystyki napraw i wraca do stanu UP
                repair_duration = self.current_time - responsible_server.fail_time
                self.total_repair_time += repair_duration
                self.repair_count += 1
                responsible_server.fail_time = None
                responsible_server.start_life()

            # Określenie nowego stanu klastra po zdarzeniu
            current_cluster_state = self.get_cluster_state()