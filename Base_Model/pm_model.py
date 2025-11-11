from server import Server
import numpy as np

SIM_DURATION = 8760.0

class PM_Model_Engine:
    def __init__(self, servers=None):
        self.current_time = 0.0

        if servers is not None:
            self.servers = servers
        else:
            self.servers = [Server(i) for i in range(1, 4)]


        self.state_durations = {'S3': 0.0, 'S2': 0.0, 'S1': 0.0, 'S0': 0.0}
        self.num_failures = 0
        self.repair_count = 0
        self.total_repair_time = 0.0

        #  Nowe zmienne dla PM
        self.PM_INTERVAL = 100.0  #  ile godzin przegląd techniczny
        self.PM_DURATION = 2.0    # jak długo trwa PM
        self.pm_count = 0
        self.total_pm_time = 0.0

        # Inicjalizacja czasu do pierwszego PM
        for s in self.servers:
            s.next_pm_due = np.random.uniform(0, self.PM_INTERVAL)
            s.pm_duration = 0.0

    def get_cluster_state(self):
        #Serwer w stanie DOWN lub PM = niedostępny
        num_available = sum(1 for s in self.servers if s.state not in ["DOWN", "PM"])

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

            for s in self.servers:
                # Awaria
                if s.state == "UP" and 0 < s.ttf_remaining < next_event_time:
                    next_event_time = s.ttf_remaining
                    event_type = "FAILURE"
                    responsible_server = s
                # Planowa konserwacja
                elif s.state == "UP" and 0 < s.next_pm_due < next_event_time:
                    next_event_time = s.next_pm_due
                    event_type = "PM_START"
                    responsible_server = s
                # Koniec naprawy
                elif s.state == "DOWN" and 0 < s.ttr_duration < next_event_time:
                    next_event_time = s.ttr_duration
                    event_type = "REPAIR_END"
                    responsible_server = s
                # Koniec PM
                elif s.state == "PM" and 0 < s.pm_duration < next_event_time:
                    next_event_time = s.pm_duration
                    event_type = "PM_END"
                    responsible_server = s

            if self.current_time + next_event_time >= SIM_DURATION:
                self.update_state_duration(current_cluster_state, SIM_DURATION - self.current_time)
                self.current_time = SIM_DURATION
                break

            # Aktualizacja czasu
            self.update_state_duration(current_cluster_state, next_event_time)
            self.current_time += next_event_time

            # Aktualizacja pozostałych czasów
            for s in self.servers:
                if s.state == "UP":
                    s.ttf_remaining = max(0.0, s.ttf_remaining - next_event_time)
                    s.next_pm_due = max(0.0, s.next_pm_due - next_event_time)
                elif s.state == "DOWN":
                    s.ttr_duration = max(0.0, s.ttr_duration - next_event_time)
                elif s.state == "PM":
                    s.pm_duration = max(0.0, s.pm_duration - next_event_time)

            # Obsługa zdarzeń
            if event_type == "FAILURE":
                responsible_server.fail()
                responsible_server.fail_time = self.current_time
                self.num_failures += 1

            elif event_type == "REPAIR_END":
                repair_duration = self.current_time - responsible_server.fail_time
                self.total_repair_time += repair_duration
                self.repair_count += 1
                responsible_server.start_life()

            elif event_type == "PM_START":
                responsible_server.state = "PM"
                responsible_server.pm_duration = self.PM_DURATION
                responsible_server.next_pm_due = 0.0
                self.pm_count += 1

            elif event_type == "PM_END":
                responsible_server.start_life()
                responsible_server.state = "UP"
                self.total_pm_time += self.PM_DURATION
                responsible_server.next_pm_due = self.PM_INTERVAL

            current_cluster_state = self.get_cluster_state()

    def get_results(self):
        availability = 1 - (self.state_durations['S1'] + self.state_durations['S0']) / SIM_DURATION
        return {
            "availability": availability,
            "failures": self.num_failures,
            "repairs": self.repair_count,
            "pm_count": self.pm_count,
            "total_pm_time": self.total_pm_time,
            "state_durations": self.state_durations
        }
