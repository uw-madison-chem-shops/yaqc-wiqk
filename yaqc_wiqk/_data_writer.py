import time
import pathlib
import os

import numpy as np
import tidy_headers

from ._timestamp import TimeStamp


class DataWriter(object):
    def __init__(self, main_window):
        self._main_window = main_window

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
        headers["columns"] = ["timestamp",
                              "valve_0",
                              "valve_1",
                              "valve_2",
                              "valve_3",
                              "ai0",
                              "ai1",
                              "ai2",
                              "labjack_temperature",
                              ]
        tidy_headers.write(self.filepath, headers)

    def write(self):
        arr = np.empty(9)
        arr[0] = time.time()
        arr[1] = 0
        arr[2] = 1
        arr[3] = 2
        arr[4] = 3
        arr[5] = 4
        arr[6] = 5
        arr[7] = 7
        arr[8] = 9
        with open(self.filepath, "a") as f: 
            np.savetxt(f, arr.T, delimiter="\t", newline="\t", fmt="%.6f")
            f.write("\n")
