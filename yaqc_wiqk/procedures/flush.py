# flush


import time
import yaqc

from .._pump import *


def run():
    # Flush
    # (all volumes in mL unless specified differently

    # pall_flow_rates is the flow rate of one DSP

    # FILL IN PUMP FLOW RATE BELOW
    pall_flow_rates = 10  # [10,20, 30, 40, 50] (mL/min)
    pall_flow_rates_mL_s = pall_flow_rates / 60  # (mL/s)

    # Reactor Parameters
    Vsl = 1.94
    Veq = 0.715
    Vrxnzone = 9.975
    Vexit = 0.393
    Veq_quench = 1.2
    valve_open_time = 1

    # Median exit time calc w/ pumps flow rates
    if pall_flow_rates == 10:
        median_exit_time = 48.2
    elif pall_flow_rates == 20:
        median_exit_time = 24.6
    elif pall_flow_rates == 30:
        median_exit_time = 16.8
    elif pall_flow_rates == 40:
        median_exit_time = 12.8
    elif pall_flow_rates == 50:
        median_exit_time = 10.6

    # Valve assignments (A= run reactions, B= refill SL and DSPs)
    valve0 = yaqc.Client(36000)  # sample collection valve (A= sample, B=waste)
    valve1 = yaqc.Client(36001)  # Monomer
    valve2 = yaqc.Client(36002)  # Catalyst
    valve3 = yaqc.Client(36003)  # Quench
    # Pump assignments
    p1 = Pump(1)  # Monomer line
    p2 = Pump(2)  # Catalyst line
    p3 = Pump(4)  # Quench line

    # Pump injection volume for rxn
    pall_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    # Pump parameters for flush (extra step for DSPs multi-step mode)
    pall_flush_inj = 0.1
    pall_flush_rates = 10
    pump_run_time = pall_rxn_inj / pall_flow_rates_mL_s

    print("run time " + str(round((pump_run_time / 60), 1)) + " min")

    # Open Mon, Cat, & Quench valves
    valve1.set_identifier("A")
    while valve1.busy():
        continue
    assert valve1.get_identifier() == "A"
    valve2.set_identifier("A")
    while valve2.busy():
        continue
    assert valve2.get_identifier() == "A"
    valve3.set_identifier("A")
    while valve3.busy():
        continue
    assert valve3.get_identifier() == "A"

    # Collection valve to waste first
    valve0.set_identifier("B")
    while valve0.busy():
        continue

    assert valve0.get_identifier() == "B"
    # Prompt the User (y/n)
    # def yes_or_no(question):
        # answer = input(question + "(y/n): ").lower().strip()
        # print("")
        # while not (answer == "y" or answer == "yes" or answer == "n" or answer == "no"):
            # print("Input yes or no")
            # answer = input(question + "(y/n):").lower().strip()
            # print("")
        # if answer[0] == "y":
            # return True
        # else:
            # return False

    # if yes_or_no("Are you sure you want to FLUSH the reactor?"):
        # print("Starting Flush")
    # else:
        # print("Flush Stopped")
        # exit()
        # print("Error")  # checking exit()

    # Pump instructions for reaction, flush, and refill (Cat & Mon the same)
    p1.add_step(volume=pall_rxn_inj, rate=pall_flow_rates, delay=0)
    p1.add_step(volume=pall_flush_inj, rate=pall_flush_rates, delay=0)

    p2.add_step(volume=pall_rxn_inj, rate=pall_flow_rates, delay=0)
    p2.add_step(volume=pall_flush_inj, rate=pall_flush_rates, delay=0)
    # Quench needs additioal quench delay
    p3.add_step(volume=pall_rxn_inj, rate=pall_flow_rates, delay=0)
    p3.add_step(volume=pall_flush_inj, rate=pall_flush_rates, delay=0)

    start_pumps(1, 2, 4)

    # Collection valve timing and instructions
    time.sleep(pump_run_time / 2)
    valve0.set_identifier("A")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "A"
    time.sleep(valve_open_time)
    valve0.set_identifier("B")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "B"

    # Set valves back to B for refill
    time.sleep(pump_run_time)
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
    valve0.set_identifier("B")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "B"

    print("Flush Complete")
