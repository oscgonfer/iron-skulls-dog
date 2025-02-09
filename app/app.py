from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit,
                                QVBoxLayout, QHBoxLayout, QWidget)
from PyQt6.QtCore import QProcess
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.process = None
        self.play = None

        self.process_button = QPushButton("Start server")
        self.process_button.pressed.connect(self.start_process)
        self.process_logger = QPlainTextEdit()
        self.process_logger.setReadOnly(True)
        l = QVBoxLayout()
        l.addWidget(self.process_button)
        l.addWidget(self.process_logger)

        self.play_button = QPushButton("Send capture")
        self.play_button.pressed.connect(self.start_play)
        self.play_logger = QPlainTextEdit()
        self.play_logger.setReadOnly(True)
        l.addWidget(self.play_button)
        l.addWidget(self.play_logger)

        w = QWidget()
        w.setLayout(l)

        self.setCentralWidget(w)

    def process_message(self, s):
        self.process_logger.appendPlainText(s)

    def play_message(self, s):
        self.play_logger.appendPlainText(s)

    def start_process(self):
        if self.process is None:  # No process running.
            self.process_message("Executing process")
            self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.process.readyReadStandardOutput.connect(self.handle_process_stdout)
            self.process.readyReadStandardError.connect(self.handle_process_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)  # Clean up once complete.
            self.process.start("python", ['main.py'])

    def start_play(self):
        if self.play is None:  # No process running.
            self.play_message("Playing file")
            self.play = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.play.readyReadStandardOutput.connect(self.handle_play_stdout)
            self.play.readyReadStandardError.connect(self.handle_play_stderr)
            self.play.finished.connect(self.play_finished)  # Clean up once complete.
            self.play.start("python", ['play_capture.py', '--capture-file', 'capture/POPO.cap'])

    def handle_process_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.process_message(stderr)

    def handle_process_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.process_message(stdout)

    def handle_play_stderr(self):
        data = self.play.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.play_message(stderr)

    def handle_play_stdout(self):
        data = self.play.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.play_message(stdout)

    def handle_state(self, state):
        self.process_message(f"State changed: {state}")

    def process_finished(self):
        self.process_message("Process finished.")
        self.process = None

    def play_finished(self):
        self.play_message("Play finished.")
        self.play = None

app = QApplication(sys.argv)

w = MainWindow()
w.show()

app.exec()