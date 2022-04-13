import time
import threading


class ProcedureRunner(object):
    def __init__(self, main_window):
        self._main_window = main_window

    def run(self, path):
        def wait_10():
            self._main_window.procedure_started.emit()
            for i in range(120):
                print(i)
                time.sleep(1)
            self._main_window.procedure_finished.emit()

        threading.Thread(target=wait_10).start()
