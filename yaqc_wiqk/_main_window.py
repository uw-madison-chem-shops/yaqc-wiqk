#! /usr/bin/env python

import sys
import os
import pathlib
import matplotlib
import time

from qtpy import QtWidgets, QtCore
import appdirs
import toml
import yaqc
import qtypes

from .__version__ import __version__
from ._procedure_runner import ProcedureRunner
from ._timestamp import TimeStamp


matplotlib.use("ps")  # important - images will be generated in worker threads

__here__ = pathlib.Path(os.path.abspath(__file__)).parent


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()
    procedure_started = QtCore.Signal()  # emitted by procedure_runner
    procedure_finished = QtCore.Signal()  # emitted by procedure_runner

    def __init__(self, config):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-wiqk")
        self._create_main_frame()
        self._procedure_runner = ProcedureRunner(self)
        self._last_procedure_started = float("nan")
        self._poll_timer = QtCore.QTimer(interval=1000)  # one second
        self._poll_timer.timeout.connect(self._poll)
        self.procedure_started.connect(self._on_procedure_started)
        self.procedure_finished.connect(self._on_procedure_finished)

    def _create_main_frame(self):
        splitter = QtWidgets.QSplitter()
        # tree ------------------------------------------------------------------------------------
        self._tree_widget = qtypes.TreeWidget(width=500)
        splitter.addWidget(self._tree_widget)
        # valves
        heading = qtypes.Null("valves")
        self._tree_widget.append(heading)
        for i in range(4):
            heading.append(qtypes.Enum(str(i), value={"allowed": ["A", "B"]}))
        # procedures
        self._procedures_enum = qtypes.Enum(
            "procedures", value={"allowed": ["continuous flow", "stopped flow", "flush", "refill"]}
        )
        self._tree_widget.append(self._procedures_enum)
        self._procedures_enum.updated.connect(self._on_procedures_enum_updated)
        # tabs ------------------------------------------------------------------------------------
        self._tab_widget = QtWidgets.QTabWidget()
        self._script_display_widget = QtWidgets.QTextEdit(readOnly=True)
        self._tab_widget.addTab(self._script_display_widget, "script")
        self._tab_widget.addTab(QtWidgets.QWidget(), "graph")
        splitter.addWidget(self._tab_widget)
        # finish ----------------------------------------------------------------------------------
        self.setCentralWidget(splitter)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 50)
        self._tree_widget.expandAll()
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)
        self._on_procedures_enum_updated()

    def _on_procedures_enum_updated(self):
        new_procedure = self._procedures_enum.get_value()
        if new_procedure == "continuous flow":
            self._procedures_enum.clear()
            self._procedures_enum.append(qtypes.Float("flow rate (mL/min)", value={"value": 10}))
            self._procedures_enum.append(qtypes.Float("reaction time (s)", value={"value": 60}))
            pass
        elif new_procedure == "stopped flow":
            self._procedures_enum.clear()
            self._procedures_enum.append(qtypes.Float("flow rate (mL/min)"))
            self._procedures_enum.append(qtypes.Float("reaction time (s)"))

        elif new_procedure == "flush":
            self._procedures_enum.clear()

        elif new_procedure == "refill":
            self._procedures_enum.clear()

        else:
            print(f"procedure {new_procedure} not recognized in _on_procedures_enum_updated")
            return
        self._run_button = qtypes.Button("run")
        self._run_button.updated.connect(self._on_run_button_updated)
        self._procedures_enum.append(self._run_button)
        self._time_elapsed_widget = qtypes.String("time elapsed (min:sec)", disabled=True)
        self._procedures_enum.append(self._time_elapsed_widget)
        self._data_filepath_widget = qtypes.String("data filepath", disabled=True)
        self._procedures_enum.append(self._data_filepath_widget)
        # update script display
        path = __here__ / "procedures" / f"{new_procedure.replace(' ', '_')}.py"
        with open(path, "r") as f:
            self._script_display_widget.setText(f.read())

    def _on_procedure_finished(self):
        print("_on_procedure_finished")
        self._poll_timer.stop()

    def _on_procedure_started(self):
        print("_on_procedure_started")

    def _on_run_button_updated(self):
        procedure = self._procedures_enum.get_value()
        self._last_procedure_started = time.time()
        # make data file
        filename = TimeStamp(at=self._last_procedure_started).path + f" {procedure}.txt"
        self._data_filepath = pathlib.Path(os.path.expanduser("~")) / "WiQK-data" / filename
        self._data_filepath_widget.set_value(str(self._data_filepath))
        # start data recording
        self._poll_timer.start()
        # launch procedure
        self._procedure_runner.run(None)

    def _poll(self):
        minutes, seconds = divmod(time.time() - self._last_procedure_started, 60)
        minutes = str(round(minutes)).zfill(2)
        seconds = str(round(seconds)).zfill(2)
        self._time_elapsed_widget.set_value(f"{minutes}:{seconds}")
        print("poll")
