from cluster_engine import Base_Model_Engine
from pm_model import PM_Model_Engine
from server import Server
import copy
import numpy as np

def compare_models_shared_servers():
    seed = np.random.randint(0, 1000000)
    np.random.seed(seed)
    servers = [Server(i) for i in range(1, 4)]

    base_servers = copy.deepcopy(servers)
    pm_servers = copy.deepcopy(servers)

    base = Base_Model_Engine(servers=base_servers)
    base.run_simulation()
    base_result = base.get_results() if hasattr(base, 'get_results') else {
        "availability": 1 - (base.state_durations["S1"] + base.state_durations["S0"]) / 8760.0,
        "failures": base.num_failures,
        "repairs": base.repair_count
    }

    pm = PM_Model_Engine(servers=pm_servers)
    pm.run_simulation()
    pm_result = pm.get_results()

    print("\n=== Porównanie modeli (te same dane serwerów) ===")
    print(f"Bez PM: dostępność = {base_result['availability']:.6f}, awarii = {base_result['failures']}")
    print(f"Z PM:   dostępność = {pm_result['availability']:.6f}, awarii = {pm_result['failures']}, PM = {pm_result['pm_count']}")
    delta = (pm_result['availability'] - base_result['availability']) * 10000
    print(f"Poprawa dostępności: {delta:+.2f} ×10⁻⁴")

if __name__ == "__main__":
    compare_models_shared_servers()
