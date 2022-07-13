# continuous flow


def run(flow_rate):
    import time
    import yaqc
    from .._pump import Pump, start_pumps

    # Median exit times (i.e., exit time for CONTINUOUS FLOW) needed to determine collection valve timing
    # 50mL/min, 0.833 mL/sec, tmed = 10.6 sec
    # 40mL/min, 0.667 mL/sec, tmed =  12.8 sec
    # 30mL/min, 0.5 mL/sec, tmed = 16.8 sec
    # 20mL/min, 0.333 mL/sec, tmed = 24.6 sec
    # 10mL/min, 0.167 mL/sec, tmed = 48.2

    # define variables to determine collection window
    median_exit_time = 16.8
    flow_rates = (flow_rate/60)
    Vsl = 1.94
    Veq = 0.715
    Vrxnzone = 9.975
    Vexit = 0.393
    Veq_quench = 1.2
    valve_open_time = 0.6
    # Pump parameters for rxn
    p1_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    p2_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    p3_rxn_inj = 2.5 * Vsl + Veq + 0.5 * Vrxnzone + 0.333 * Vexit
    pall_flow_rates = flow_rates * 60
    # Pump parameters for flush
    p1_flush_inj = 0.1
    p2_flush_inj = 0.1
    p3_flush_inj = 0.1
    pall_flush_rates = 10
    pump_run_time = p1_rxn_inj / flow_rates
    flush_valve_delay = pump_run_time

    # Calculate collection window
    collection_window = median_exit_time - 0.5

    # calculate theoretical time for front of rxn plug to reach BBM 2, then
    # subtract the amount of time that the front of the quench plug takes to get to BBM2
    quench_delay = Veq / flow_rates + Vrxnzone / (2 * flow_rates) - Veq_quench / flow_rates

    # calculate time pumps need to wait before flushing
    pump_flush_delay = median_exit_time

    # calculate time pump need to wait before refilling
    refill_delay = pump_flush_delay + 5

    # calculate pump run time before flush
    print("Start collection window =  " + str(collection_window))
    print("Quench delay = " + str(round(quench_delay)))
    print("Pump flush delay = " + str(pump_flush_delay))
    print("Real flush valve delay " + str(collection_window + 1 + flush_valve_delay))
    print("Refill delay = " + str(refill_delay))
    print("Pump run time " + str(pump_run_time))

    # Pump parameters for refill
    p1_refill_vol = p1_rxn_inj + p1_flush_inj
    p2_refill_vol = p2_rxn_inj + p2_flush_inj
    p3_refill_vol = p3_rxn_inj + p3_flush_inj
    p1_refill_delay = refill_delay + 1
    p2_refill_delay = refill_delay + 1
    p3_refill_delay = refill_delay + 1
    pall_refill_rates = -2.5
    refill_valve_delay = refill_delay

    print("Pump refill delay " + str(p1_refill_delay))

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

    import time

    p1 = Pump(1)
    p2 = Pump(2)
    p3 = Pump(4)

    p1.add_step(volume=p1_rxn_inj, rate=pall_flow_rates, delay=0)
    p1.add_step(volume=p1_flush_inj, rate=pall_flush_rates, delay=round(pump_flush_delay))
    p1.add_step(volume=p1_refill_vol, rate=pall_refill_rates, delay=round(p1_refill_delay))

    p2.add_step(volume=p2_rxn_inj, rate=pall_flow_rates, delay=0)
    p2.add_step(volume=p2_flush_inj, rate=pall_flush_rates, delay=round(pump_flush_delay))
    p2.add_step(volume=p2_refill_vol, rate=pall_refill_rates, delay=round(p2_refill_delay))

    p3.add_step(volume=p3_rxn_inj, rate=pall_flow_rates, delay=quench_delay)
    p3.add_step(volume=p3_flush_inj, rate=pall_flush_rates, delay=round((pump_flush_delay - quench_delay)))
    p3.add_step(volume=p3_refill_vol, rate=pall_refill_rates, delay=round(p3_refill_delay))

    start_pumps(1, 2, 4)

    # Collection valve timing and instructions

    time.sleep(collection_window)
    valve0.set_identifier("A")
    while valve0.busy():
        continue
    assert valve0.get_identifier() == "A"

    time.sleep(valve_open_time)
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
