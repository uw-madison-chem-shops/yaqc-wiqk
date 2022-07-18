#! /usr/bin/env python

import sys
import os
import pathlib
import time
from dataclasses import dataclass
import functools

import matplotlib
from qtpy import QtWidgets, QtCore
import appdirs
import toml
import yaqc
import qtypes
import tidy_headers
from yaqc_qtpy import QClient

from .__version__ import __version__
from ._procedure_runner import ProcedureRunner
from ._data_writer import DataWriter
from . import procedures
from ._config import Config
from ._valve import Valve


config = Config()

matplotlib.use("ps")  # important - images will be generated in worker threads

__here__ = pathlib.Path(os.path.abspath(__file__)).parent


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()
    procedure_started = QtCore.Signal()  # emitted by procedure_runner
    procedure_finished = QtCore.Signal()  # emitted by procedure_runner

    def __init__(self, config):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-wiqk")
        self._connect_to_valves()
        self._create_main_frame()
        self._procedure_runner = ProcedureRunner(self)
        self._data_writer = DataWriter(self)
        self._last_procedure_started = float("nan")
        self._poll_timer = QtCore.QTimer(interval=1000)  # one second
        self._poll_timer.timeout.connect(self._poll)
        self.procedure_started.connect(self._on_procedure_started)
        self.procedure_finished.connect(self._on_procedure_finished)

    def _connect_to_valves(self):
        self._valves = {}
        for i in range(4):
            port = config[f"valve{i}_port"]
            self._valves[i] = Valve(port=port, index=i)

    def _create_main_frame(self):
        splitter = QtWidgets.QSplitter()
        # tree ------------------------------------------------------------------------------------
        self._tree_widget = qtypes.TreeWidget(width=500)
        splitter.addWidget(self._tree_widget)
        # valves
        heading = qtypes.Null("valves")
        self._tree_widget.append(heading)
        for data in self._valves.values():
            heading.append(data.enum)
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
        splitter.setStretchFactor(1, 2)
        self._tree_widget.expandAll()
        self._on_procedures_enum_updated()
        self._tree_widget.resizeColumnToContents(0)
        self._tree_widget.resizeColumnToContents(1)

    def _on_procedures_enum_updated(self):
        new_procedure = self._procedures_enum.get_value()
        self._kwargs = {}
        self._procedures_enum.clear()
        if new_procedure == "continuous flow":
            self._kwargs["flow_rate"] = qtypes.Float("flow rate (mL/min)", value={"value": 10})
        elif new_procedure == "stopped flow":
            self._kwargs["flow_rate"] = qtypes.Float("flow rate (mL/min)", value={"value": 10})
            self._kwargs["reaction_time"] = qtypes.Float("reaction time (s)", value={"value": 60})
        elif new_procedure == "flush":
            pass
        elif new_procedure == "refill":
            pass
        else:
            print(f"procedure {new_procedure} not recognized in _on_procedures_enum_updated")
            return
        for obj in self._kwargs.values():
            self._procedures_enum.append(obj)
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
        self._procedures_enum.disabled.emit(False)
        self._run_button.disabled.emit(False)
        for obj in self._kwargs.values():
            obj.disabled.emit(False)

    def _on_procedure_started(self):
        print("_on_procedure_started")
        self._procedures_enum.disabled.emit(True)
        self._run_button.disabled.emit(True)
        for obj in self._kwargs.values():
            obj.disabled.emit(True)

    def _on_run_button_updated(self):
        procedure = self._procedures_enum.get_value()
        self._last_procedure_started = time.time()
        # make data file
        self._data_writer.create_file(procedure=procedure,
                                      procedure_args=self._kwargs,
                                      start_time = self._last_procedure_started)
        self._data_filepath_widget.set_value(str(self._data_writer.filepath))
        # start data recording
        self._poll_timer.start()
        # launch procedure
        function = procedures.__dict__[procedure.lower().replace(" ", "_")]
        kwargs = {k: v.get_value() for k, v in self._kwargs.items()}
        self._procedure_runner.run(function, kwargs=kwargs)

    def _poll(self):
        minutes, seconds = divmod(time.time() - self._last_procedure_started, 60)
        minutes = str(round(minutes)).zfill(2)
        seconds = str(round(seconds)).zfill(2)
        self._time_elapsed_widget.set_value(f"{minutes}:{seconds}")
        print("poll")
        self._data_writer.write()
