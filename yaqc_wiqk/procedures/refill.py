# refill


import time
import yaqc

from .._pump import *


def run():
    # Refill DSPs
    # (all volumes in mL unless specified differently)

    # Reactor Volume Parameters
    Vsl = 1.94
    Veq = 0.715
    Vrxnzone = 9.975
    Vexit = 0.393

    # Valve & Pump Assignments
    valve0 = yaqc.Client(36000)  # sample collection valve
    valve1 = yaqc.Client(36001)
    valve2 = yaqc.Client(36002)
    valve3 = yaqc.Client(36003)
    p1 = Pump(1)
    p2 = Pump(2)
    p3 = Pump(4)

    # Pump Injection Volume for rxn/refill
    p1_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    p2_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    p3_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    # Pump parameters for refill, refill vol = rxn vol
    p1_refill_vol = p1_rxn_inj
    p2_refill_vol = p2_rxn_inj
    p3_refill_vol = p3_rxn_inj
    
    # Pump Injection Volume for extra step for DSPs multi-step mode
    p1_extra_inj = 0.1
    p2_extra_inj = 0.1
    p3_extra_inj = 0.1
    # Pump refill rates (mL/min)
    pall_refill_rates = -2.5
    pall_refill_rates_mL_s = pall_refill_rates / 60
    pump_run_time = p1_rxn_inj / -pall_refill_rates_mL_s

    print("run time " + str(round((pump_run_time / 60), 1)) + " min")

    # Total volume withdraw by 1 pump
    Vtotal_1P = p1_refill_vol + p1_extra_inj

    # Refill valve timing and instructions
    valve1.set_identifier("B")
    while valve1.busy():
        continue
    assert valve1.get_identifier() == "B"

    valve2.set_identifier("B")
    while valve2.busy():
        continue
    assert valve2.get_identifier() == "B"

    valve3.set_identifier("B")
    while valve3.busy():
        continue
    assert valve3.get_identifier() == "B"

    p1.add_step(volume=p1_refill_vol, rate=pall_refill_rates, delay=0)
    p1.add_step(volume=p1_extra_inj, rate=pall_refill_rates, delay=0)
    p2.add_step(volume=p2_refill_vol, rate=pall_refill_rates, delay=0)
    p2.add_step(volume=p2_extra_inj, rate=pall_refill_rates, delay=0)
    p3.add_step(volume=p3_refill_vol, rate=pall_refill_rates, delay=0)
    p3.add_step(volume=p3_extra_inj, rate=pall_refill_rates, delay=0)

    start_pumps(1, 2, 4)
    print("Refill rate = " + str(-pall_refill_rates) + " mL/min")
    print("Volume withdraw per pump = " + str(Vtotal_1P) + " mL")
    time.sleep(pump_run_time + 1)
    print("Refill Complete")
