__all__ = ["Pump", "start_pumps"]


import time
import serial
import operator
import functools

from ._config import Config


config = Config()


try:
    ser = serial.Serial(config["pump_port"], baudrate=19200)
except:
    ser = None
    print("Could not open pump serial port!")


class Pump(object):
    instances = {}

    def __init__(self, index):
        self.index = index
        self.steps = []
        self.instances[index] = self

    def clear_steps(self):
        self.steps = []

    def add_step(self, volume, rate, delay):
        d = {"volume": volume, "rate": rate, "delay": delay}
        self.steps.append(d)

    def write_steps_to_pump(self):
        # volume
        vs = ",".join([str(s["volume"]) for s in self.steps])
        ser.write(f"{self.index}:set volume {vs}\r".encode())
        time.sleep(2)
        # rate
        rs = ",".join([str(s["rate"]) for s in self.steps])
        ser.write(f"{self.index}:set rate {rs}\r".encode())
        time.sleep(2)
        # delay
        ds = ",".join([str(s["delay"]) for s in self.steps])
        ser.write(f"{self.index}:set delay {ds}\r".encode())
        time.sleep(2)


def start_pumps(*idxs):
    for idx in idxs:
        Pump.instances[idx].write_steps_to_pump()
    index = functools.reduce(operator.__or__, idxs)
    ser.write(f"{index}:start\r".encode())
