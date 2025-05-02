from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit,
                                QVBoxLayout, QHBoxLayout, QWidget)
from PySide6.QtCore import QProcess
import sys
from ui_form import Ui_MainWindow
from os.path import join, exists, abspath

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.process = None
        self.play = None

        self.ui.pushButton_connect.pressed.connect(self.connect)
        self.ui.pushButton_stop.pressed.connect(self.disconnect)

    def message(self, s):
        self.ui.logger.appendPlainText(s)

    def connect(self):
        if self.process is None:
            self.message("Executing process")
            self.process = QProcess()
            self.process.read
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.finish)
            path = abspath('.')
            self.process.start("python", [join(path,'main.py'), '--broadcast', '--dry-run'])

    def disconnect(self):
        if self.process is not None:
            self.finish()

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.message(data)
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.message(data)
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        print (state)
        self.message(f"State changed: {state}")

    def finish(self):
        self.message("Process finished.")
        self.process = None

if __name__ == "__main__":
    app = QApplication([])

    widget = MainWindow()
    widget.setWindowTitle("Iron Dog")

    widget.show()
    app.exec()