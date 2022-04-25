import time
import threading
import functools


class ProcedureRunner(object):
    def __init__(self, main_window):
        self._main_window = main_window

    def run(self, function, kwargs):
        def worker(main_window, function, kwargs):
            main_window.procedure_started.emit()
            function(**kwargs)
            main_window.procedure_finished.emit()

        partial = functools.partial(worker, self._main_window, function, kwargs)

        threading.Thread(target=partial).start()
