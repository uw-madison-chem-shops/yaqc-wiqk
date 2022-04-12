#! /usr/bin/env python


import matplotlib

matplotlib.use("ps")  # important - images will be generated in worker threads

import sys
from PySide2 import QtWidgets, QtCore

app = QtWidgets.QApplication(sys.argv)

import os
import pathlib


import appdirs
import toml

import yaqc


from .__version__ import __version__


class MainWindow(QtWidgets.QMainWindow):
    shutdown = QtCore.Signal()

    def __init__(self, config):
        super().__init__(parent=None)
        self.setWindowTitle("yaqc-wiqk")
