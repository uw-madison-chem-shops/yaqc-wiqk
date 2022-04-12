#!/usr/bin/env python3

import os
import pathlib
import subprocess
import sys
from qtpy import QtWidgets

import appdirs  # type: ignore
import click
import toml

from .__version__ import __version__
from ._main_window import MainWindow


@click.command()
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(input)
    window.show()
    window.showMaximized()
    app.exec_()


if __name__ == "__main__":
    main()
