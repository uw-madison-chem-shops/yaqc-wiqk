# stopped flow


import time
import yaqc

from .._pump import *


def run(flow_rate, reaction_time):
    # Mean residence time needed to place middle of plug in middle of rxn zone before rxn delay
    # 50mL/min, 0.833 mL/sec, tm = 2.06 sec
    # 40mL/min, 0.667 mL/sec, tm = 2.65 sec
    # 30mL/min, 0.5 mL/sec, tm = 3.72 sec
    # 20mL/min, 0.333 mL/sec, tm = 6.8 sec
    # 10mL/min, 0.167 mL/sec, tm = 12.9 sec

    # Median exit times (i.e., exit time for STOPPED FLOW, supposed to account for pump
    # acceleration/deceleration) needed to determine collection valve timing
    # Updated 01.04.2022

    # 50mL/min, 0.833 mL/sec, tmed = 12.4 sec
    # 40mL/min, 0.667 mL/sec, tmed =  14.2
    # 30mL/min, 0.5 mL/sec, tmed = 17.6 sec (not updated, using 18.2 as guess)
    # 20mL/min, 0.333 mL/sec, tmed = 25.5 (not updated)
    # 10mL/min, 0.167 mL/sec, tmed = 49 sec (not updated)
    Vsl = 1.94
    Veq = 0.715
    Vrxnzone = 9.975
    Vexit = 0.393
    Veq_quench = 1.2

    # define variables to determine collection window rxn time, and pump timing
    mean_residence_time = 3.72
    median_exit_time = 17.6
    pall_flow_rates = flow_rate  #mL/min
    flow_rates = pall_flow_rates / 60  #mL/sec
    
    cont_flow_residence_t = (Vrxnzone/(2*flow_rates)) #sec
    rxn_delay = reaction_time - cont_flow_residence_t
    print("Reaction delay:  " + str(round(rxn_delay, 5)) + " sec")
    
    p1_rxn_delay = rxn_delay
    p2_rxn_delay = rxn_delay
    p3_rxn_delay = rxn_delay


    # Pump parameters for rxn. Different than continuous flow because middle of plug needs to be stopped in middle of rxn zone.
    # rxn injection volumes are calculated as (middle of plug + equlibration loop + 1/4 rxn zone volume). the last term
    # (1/4 rxn zone volumes) adds up to 1/2 of rxn zone volume because two pump streams are combining

    full_exit_vol = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    p1_rxn_inj = mean_residence_time * flow_rates + Veq + 0.25 * Vrxnzone
    p2_rxn_inj = mean_residence_time * flow_rates + Veq + 0.25 * Vrxnzone
    p3_rxn_inj = full_exit_vol

    s2_p1_rxn_inj = full_exit_vol - p1_rxn_inj
    s2_p2_rxn_inj = full_exit_vol - p2_rxn_inj
    s2_p3_rxn_inj = full_exit_vol - p3_rxn_inj + 0.1
    # Pump parameters for flush
    p1_flush_inj = 0.1
    p2_flush_inj = 0.1
    p3_flush_inj = 0.1
    pall_flush_rates = 10
    pump_run_time = p1_rxn_delay + full_exit_vol / flow_rates
    flush_valve_delay = pump_run_time

    print("DSP Flow Rate =  " + str(round(pall_flow_rates, 1)) + " mL/min")
    print("Median exit time set to:  " + str(round(median_exit_time, 1)) + " sec")

    # print("Catlalyst first injection volume " + str(round(p1_rxn_inj,2)) + " mL")
    # print("Monomer first injection volume " + str(round(p2_rxn_inj,2)) + " mL")
    # print("Quench first injection Volume " + str(round(p3_rxn_inj,2)) + " mL")

    # Calculate collection window
    collection_window = p1_rxn_delay + median_exit_time - 0.3

    print("Exit valve opens after:  " + str(round(collection_window, 2)) + " sec")

    # calculate theoretical time for front of rxn plug to reach BBM 2, then
    # subtract the amount of time that the front of the quench plug takes to get to BBM2. You want quench pump to start early enough to make
    # up the time needed to travel through its own equilibration loop, and arrive at BBM2 at the same time the rxn plug gets to BBM2
    quench_delay = (
        p1_rxn_delay + Veq / flow_rates + Vrxnzone / (2 * flow_rates) - Veq_quench / flow_rates
    )

    # print("Quench delay = " + str(quench_delay))

    # calculate time pumps need to wait before flushing
    pump_flush_delay = (
        p1_rxn_delay
        + mean_residence_time
        + ((Vsl + Veq) / flow_rates + (Vrxnzone / (2 * flow_rates)) + (Vexit / (3 * flow_rates)))
    )
    #
    p3_flush_delay = pump_flush_delay - (p3_rxn_inj - s2_p1_rxn_inj) / flow_rates
    # print("Pump flush delay = " + str(pump_flush_delay))
    # print("Real flush valve delay " + str(collection_window + 1 + flush_valve_delay))
    # calculate time pump need to wait before refilling
    refill_delay = (
        p1_rxn_delay
        + mean_residence_time
        + ((Vsl + Veq) / flow_rates + (Vrxnzone / (2 * flow_rates)) + (Vexit / (3 * flow_rates)))
        + 5
    )
    # print("Refill delay = " + str(refill_delay))

    # calculate pump run time before flush
    # print ("Pump run time " + str(pump_run_time))

    # Pump parameters for refill
    p1_refill_vol = p1_rxn_inj + s2_p1_rxn_inj + p1_flush_inj
    p2_refill_vol = p2_rxn_inj + s2_p2_rxn_inj + p2_flush_inj
    p3_refill_vol = p3_rxn_inj + s2_p3_rxn_inj + p3_flush_inj
    p1_refill_delay = refill_delay + 1
    p2_refill_delay = refill_delay + 1
    p3_refill_delay = refill_delay + 1
    pall_refill_rates = -2.5
    refill_valve_delay = refill_delay

    valve0 = yaqc.Client(36000)
    valve1 = yaqc.Client(36001)
    valve2 = yaqc.Client(36002)
    valve3 = yaqc.Client(36003)

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

    # Pump instructions for reaction, flush, and refill

    p1 = Pump(1)
    p2 = Pump(2)
    p3 = Pump(4)

    p1.add_step(volume=p1_rxn_inj, rate=pall_flow_rates, delay=0)
    p1.add_step(volume=s2_p1_rxn_inj, rate=pall_flow_rates, delay=p1_rxn_delay)
    p1.add_step(volume=p1_flush_inj, rate=pall_flush_rates, delay=round(pump_flush_delay))
    p1.add_step(volume=p1_refill_vol, rate=pall_refill_rates, delay=round(p1_refill_delay))

    p2.add_step(volume=p2_rxn_inj, rate=pall_flow_rates, delay=0)
    p2.add_step(volume=s2_p2_rxn_inj, rate=pall_flow_rates, delay=p2_rxn_delay)
    p2.add_step(volume=p2_flush_inj, rate=pall_flush_rates, delay=round(pump_flush_delay))
    p2.add_step(volume=p2_refill_vol, rate=pall_refill_rates, delay=round(p2_refill_delay))

    p3.add_step(volume=p3_rxn_inj, rate=pall_flow_rates, delay=quench_delay)
    p3.add_step(volume=s2_p3_rxn_inj, rate=pall_flow_rates, delay=0)
    p3.add_step(volume=p3_flush_inj, rate=pall_flush_rates, delay=round(p3_flush_delay))
    p3.add_step(volume=p3_refill_vol, rate=pall_refill_rates, delay=round(p3_refill_delay))

    start_pumps(1, 2, 4)

    # Collection valve timing and instructions

    time.sleep(collection_window)
    valve0.set_identifier("A")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "A"

    time.sleep(0.6)
    valve0.set_identifier("B")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "B"

    # Flush valve timing and instructions

    time.sleep(flush_valve_delay)
    valve0.set_identifier("A")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "A"

    # Refill valve timing and instructions
    time.sleep(refill_delay)
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
