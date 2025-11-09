import numpy as np
from weibull_model import generate_server_ttf
from ttr_model import generate_corrective_ttr

SIMULATION_TIME = 8766.0  # 1 rok w godzinach
NUM_SERVERS = 3  # N+1 = 3 serwery

COST_OF_DOWNTIME_PER_HOUR = 15625.0  # Koszt niedostępności (w PLN/godz.)
COST_OF_CORRECTIVE_REPAIR = 5000.0  # Jednostkowy koszt naprawy korekcyjnej (PLN)

SLA_DOWNTIME_LIMIT_MIN = 52.56  # Limit w minutach
SLA_DOWNTIME_LIMIT_HOURS = SLA_DOWNTIME_LIMIT_MIN / 60.0  # Limit w godzinach (~0.876h)
SLA_VIOLATION_PENALTY = 50000.0  # Kara za naruszenie SLA (PLN)

NUM_ITERATIONS = 1000  # Ile razy uruchomimy symulację

SERVER_NAMES = ["A", "B", "C"]


def run_corrective_simulation():

    # INICJALIZACJA ZEGARÓW I LICZNIKÓW ]
    ttf_timers = [generate_server_ttf() for _ in range(NUM_SERVERS)]
    ttr_timers = [0.0] * NUM_SERVERS

    global_time = 0.0

    # Śledzi czas niedostępności
    total_downtime_hours = 0.0

    num_failures = 0
    failed_servers_log = []

    while global_time < SIMULATION_TIME:

        # OKREŚLENIE NAJBLIŻSZEGO ZDARZENIA
        next_failure_time = min(ttf_timers)
        failure_index = ttf_timers.index(next_failure_time)

        active_repairs = [ttr for ttr in ttr_timers if ttr > 0]
        next_repare_completion = min(active_repairs) if active_repairs else SIMULATION_TIME

        delta_time = min(next_failure_time, next_repare_completion)

        # Zabezpieczenie końca symulacji
        if global_time + delta_time > SIMULATION_TIME:
            delta_time = SIMULATION_TIME - global_time
            if delta_time < 0.0001: break

        # AKTUALIZACJA CZASU I SUMOWANIE KOSZTÓW
        global_time += delta_time

        # Sprawdzenie stanu klastra (N+1)
        operational_servers = sum(1 for ttr in ttr_timers if ttr == 0)

        # Rejestrowanie niedostępności (stan S1 lub S0)
        if operational_servers < 2:
            total_downtime_hours += delta_time

        # AKTUALIZACJA LICZNIKÓW CZASU
        ttf_timers = [ttf - delta_time for ttf in ttf_timers]
        ttr_timers = [max(0, ttr - delta_time) for ttr in ttr_timers]

        # OBSŁUGA ZDARZEŃ

        # AWARIA (Serwer TTF = 0)
        if next_failure_time <= 0 and next_failure_time != float('inf'):
            # Zapisz awarię i wylosuj TTR
            num_failures += 1
            failed_servers_log.append(SERVER_NAMES[failure_index])
            ttr_generated = generate_corrective_ttr()

            # Uruchom zegar naprawy i ustaw TTF na nieskończoność
            ttr_timers[failure_index] = ttr_generated
            ttf_timers[failure_index] = float('inf')

        # KONIEC NAPRAWY (Serwer TTR = 0)
        for i in range(NUM_SERVERS):

            if ttr_timers[i] <= 0 and ttf_timers[i] == float('inf'):
                # Serwer wraca do stanu "jak nowy"  i otrzymuje nowy TTF
                new_ttf = generate_server_ttf()
                ttf_timers[i] = new_ttf
                ttr_timers[i] = 0.0

    # OBLICZENIA WYNIKOWE DLA JEDNEJ ITERACJI

    # Koszt Napraw Korekcyjnych
    total_corrective_cost = num_failures * COST_OF_CORRECTIVE_REPAIR

    # Koszt Czasu Niedostępności
    total_downtime_cost = total_downtime_hours * COST_OF_DOWNTIME_PER_HOUR

    # Kara Umowna (SLA)
    sla_penalty = 0.0
    # Porównujemy godziny niedostępności z limitem godzin
    if total_downtime_hours > SLA_DOWNTIME_LIMIT_HOURS:
        sla_penalty = SLA_VIOLATION_PENALTY

    # Całkowity Koszt
    total_financial_loss = total_corrective_cost + total_downtime_cost + sla_penalty

    # Zmieniono zwracane wartości na bardziej logiczny zestaw
    return total_financial_loss, total_downtime_hours, num_failures, total_corrective_cost, total_downtime_cost, sla_penalty, failed_servers_log


# Funkcja, która uruchamia symulację wiele razy i uśrednia wyniki
def run_monte_carlo_analysis(iterations):
    # Tworzymy puste listy do zbierania wyników z każdego uruchomienia
    all_losses = []
    all_downtimes_hours = []
    all_failures = []
    all_corrective_costs = []
    all_downtime_costs = []
    all_sla_penalties = []

    server_failure_counts = {name: 0 for name in SERVER_NAMES}

    for _ in range(iterations):
        loss, downtime_h, failures, corr_cost, downtime_cost, sla_pen, failed_log = run_corrective_simulation()

        all_losses.append(loss)
        all_downtimes_hours.append(downtime_h)
        all_failures.append(failures)
        all_corrective_costs.append(corr_cost)
        all_downtime_costs.append(downtime_cost)
        all_sla_penalties.append(sla_pen)

        for server_name in failed_log:
            server_failure_counts[server_name] += 1

    avg_total_loss = np.mean(all_losses)
    avg_downtime_hours = np.mean(all_downtimes_hours)
    avg_downtime_minutes = avg_downtime_hours * 60.0
    avg_failures = np.mean(all_failures)
    avg_corr_cost = np.mean(all_corrective_costs)
    avg_downtime_cost = np.mean(all_downtime_costs)
    avg_sla_penalty = np.mean(all_sla_penalties)

    # Procent naruszeń SLA
    violation_rate = sum(1 for penalty in all_sla_penalties if penalty > 0) / iterations * 100



    print("\nANALIZA CZASU I RYZYKA:")
    print(f"Dopuszczalny limit SLA (99.99%): {SLA_DOWNTIME_LIMIT_MIN:.2f} minut")
    print(f"Średni Czas Niedostępności Rocznie: {avg_downtime_minutes:.2f} minut ({avg_downtime_hours:.2f} godz.)")


    print(f"Procent naruszeń SLA w symulacji: {violation_rate:.2f}%")

    print("\nANALIZA AWARYJNOŚCI:")
    print(f"   Średnia liczba awarii rocznie (w całym klastrze): {avg_failures:.2f}")

    print("\nANALIZA FINANSOWA (ŚREDNIE ROCZNE KOSZTY):")
    print(f"Koszt Napraw Korekcyjnych (Awaryjnych): {avg_corr_cost:,.2f} PLN")
    print(f"Koszt Godzin Niedostępności: {avg_downtime_cost:,.2f} PLN")
    print(f"Średnia Kara Umowna (SLA): {avg_sla_penalty:,.2f} PLN")
    print("-" * 50)
    print(f"   TOTALNA ROCZNA STRATA FINANSOWA: {avg_total_loss:,.2f} PLN")
    print("-" * 50)

    return avg_total_loss, avg_downtime_hours

if __name__ == "__main__":
    run_monte_carlo_analysis(NUM_ITERATIONS)