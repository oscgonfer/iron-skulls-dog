import sys
import paho.mqtt.client as mqtt
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout
from PySide6.QtGui import QColor, QPainter, QBrush
from config import *

# Define a class for managing MQTT connection and signals
class MqttListener(QObject):
    message_received = Signal(str, str)  # topic and message

    def __init__(self, broker, port, topics):
        super().__init__()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.broker = broker
        self.port = port
        self.topics = topics

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        for topic in self.topics:
            client.subscribe(topic)
            print(f"Subscribed to {topic}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        print(f"Received message on {topic}: {message}")
        self.message_received.emit(topic, message)

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


# 7-Segment display simulation (a basic version)
class SegmentDisplay(QWidget):
    def __init__(self, value="0"):
        super().__init__()
        self.value = value
        self.setMinimumSize(150, 250)

    def set_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(QBrush(Qt.GlobalColor.white))

        # Draw the segments (A simple placeholder for a 7-segment display)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.value)
        painter.end()


# Indicator widget (colored circle for binary states or simple status)
class StatusIndicator(QWidget):
    def __init__(self, color=QColor(0, 255, 0)):
        super().__init__()
        self.color = color
        self.setMinimumSize(30, 30)
        self.setStyleSheet(f"background-color: {self.color.name()}; border-radius: 15px;")

    def set_color(self, color):
        self.color = color
        self.setStyleSheet(f"background-color: {self.color.name()}; border-radius: 15px;")


# Simple Text Display widget
class TextDisplay(QWidget):
    def __init__(self, text=""):
        super().__init__()
        self.text = text
        self.setMinimumSize(150, 30)

    def set_text(self, text):
        self.text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(QBrush(Qt.GlobalColor.white))

        # Display the text in the widget
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)
        painter.end()


# Main Window with a Grid Layout for displaying topics
class MainWindow(QMainWindow):
    def __init__(self, mqtt_listener):
        super().__init__()

        self.mqtt_listener = mqtt_listener
        self.mqtt_listener.message_received.connect(self.update_display)

        self.setWindowTitle("MQTT Display")

        # Layout for widgets (grid for topics and indicators)
        self.layout = QGridLayout()

        # Example list of topics and their associated widgets
        self.widgets = {
            "topic/temperature": SegmentDisplay("0"),
            "topic/status": StatusIndicator(QColor(255, 0, 0)),  # Red indicator by default
            "topic/message": TextDisplay("Waiting for message...")  # New TextDisplay widget
        }

        # Add widgets to the layout dynamically based on the topics
        row = 0
        for topic, widget in self.widgets.items():
            self.layout.addWidget(QLabel(f"Topic: {topic}"), row, 0)
            self.layout.addWidget(widget, row, 1)
            row += 1

        # Set central widget
        central_widget = QWidget(self)
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.resize(400, 300)

    def update_display(self, topic, message):
        """Update the display based on the MQTT topic and message"""
        print(f"Updating display for {topic}: {message}")
        if topic in self.widgets:
            widget = self.widgets[topic]

            if isinstance(widget, SegmentDisplay):
                # Map message to a value for a 7-segment display
                widget.set_value(message)
            elif isinstance(widget, StatusIndicator):
                # Map message to a color for the status indicator
                color = QColor(message)
                widget.set_color(color)
            elif isinstance(widget, TextDisplay):
                # Update text for the TextDisplay widget
                widget.set_text(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # MQTT parameters
    broker = MQTT_BROKER  # Public broker for demonstration
    port = 1883
    topics = ["topic/temperature", "topic/status", "topic/message"]

    # Create the MQTT listener
    mqtt_listener = MqttListener(broker, port, topics)

    # Connect to MQTT broker
    mqtt_listener.connect()

    # Create and show the PySide6 application window
    main_window = MainWindow(mqtt_listener)
    main_window.show()

    # Start the Qt application event loop
    sys.exit(app.exec())