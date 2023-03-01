import time
import pathlib
import os

import numpy as np
import tidy_headers
import yaqc

from ._timestamp import TimeStamp

from ._timestamp import TimeStamp


class DataWriter(object):
    def __init__(self, main_window):
        self._main_window = main_window
        self._valve_0 = yaqc.Client(36000)
        self._valve_1 = yaqc.Client(36001)
        self._valve_2 = yaqc.Client(36002)
        self._valve_3 = yaqc.Client(36003)
        self._labjack = yaqc.Client(37000)

    def create_file(self, procedure: str, procedure_args: dict, start_time: int):
        filename = TimeStamp(at=start_time).path + f" {procedure}.txt"
        self.filepath = pathlib.Path(os.path.expanduser("~")) / "WiQK-data" / filename
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.filepath.touch()
        headers = {}
        headers["timestamp"] = TimeStamp(at=start_time).RFC3339
        headers["procedure"] = procedure
        for k, v in procedure_args.items():
            headers[k] = v.get_value()
        headers["columns"] = ["timestamp",  # 0
                              "valve_0",  # 1
                              "valve_1",  # 2
                              "valve_2",  # 3
                              "valve_3",  # 4
                              "labjack_temperature",  # 5
                              "thermocouple",  # 6
                              "flux",  # 7
                              "measurement_id"  #8
                              ]
        tidy_headers.write(self.filepath, headers)

    def write(self):
        arr = np.empty(9)
        measured = self._labjack.get_measured()
        arr[0] = time.time()
        arr[1] = self._valve_0.get_position()
        arr[2] = self._valve_1.get_position()
        arr[3] = self._valve_2.get_position()
        arr[4] = self._valve_3.get_position()
        arr[5] = measured["device_temperature"]
        arr[6] = measured["temperature"]
        arr[7] = measured["flux"]
        arr[8] = measured["measurement_id"]
        with open(self.filepath, "a") as f: 
            np.savetxt(f, arr.T, delimiter="\t", newline="\t", fmt="%.6f")
            f.write("\n")
