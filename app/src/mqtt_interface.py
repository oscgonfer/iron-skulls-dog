import sys
import paho.mqtt.client as mqtt
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout
from PySide6.QtGui import QColor, QPainter, QBrush
from config import *
import json
from functools import reduce
import operator

def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value

def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]

# Define a class for managing MQTT connection and signals
class MqttListener(QObject):
    message_received = Signal(str, str)  # topic and message

    def __init__(self, broker, port, topics):
        super().__init__()
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.broker = broker
        self.port = port
        self.topics = topics

        self.client.on_connect = self.client_on_connect
        self.client.on_message = self.client_on_message

    def client_on_connect(self, client, userdata, flags, rc, properties):
        print(f"Connected with result code {rc}")
        for topic in self.topics:
            client.subscribe(topic)
            print(f"Subscribed to {topic}")

    def client_on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        print(f"Received message on {topic}: {message}")
        self.message_received.emit(topic, message)

    def connect_to_broker(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect_from_broker(self):
        self.client.loop_stop()
        self.client.disconnect()

class SegmentDisplay(QWidget):
    def __init__(self, value="0"):
        super().__init__()
        self.value = value
        # self.setMinimumSize(150, 250)
        self.color_map = color_map
        self.setStyleSheet(f"background-color: {self.color.name()}; border-radius: 15px;")

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
        self.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 800; border-radius: 15px;")

    def set_text(self, text):
        self.text = text
        self.update()
    
    def set_color(self, color):
        self.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 800; border-radius: 15px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.setPen(Qt.GlobalColor.black)
        # painter.setBrush(QBrush(Qt.GlobalColor.white))

        # Display the text in the widget
        # painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)
        painter.end()


# Main Window with a Grid Layout for displaying topics
class MainWindow(QMainWindow):
    def __init__(self, mqtt_listener, widgets):
        super().__init__()

        self.mqtt_listener = mqtt_listener
        print (self.mqtt_listener.message_received)
        self.mqtt_listener.message_received.connect(self.update_display)

        self.setWindowTitle("MQTT Display")

        # Layout for widgets (grid for topics and indicators)
        self.layout = QGridLayout()
        self.widgets = widgets

        # Add widgets to the layout dynamically based on the topics
        row = 0
        for topic in self.widgets.keys():
            for item in self.widgets[topic]:
                widget = item['widget']
                label = item['label']
                self.layout.addWidget(QLabel(label), row, 0)
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
            for item in self.widgets[topic]:
                field = item['field']
                widget = item['widget']
                color_map = None
                if 'color_map' in item:
                    color_map = item['color_map']
                
                if field is not None:
                    try:
                        js = json.loads(message)
                    except json.JSONDecodeError:
                        print ('Error decoding JSON')
                        pass
                    else:
                        msg = str(get_by_path(js, field.split('.')))
                else: 
                    msg = message

                color = "black"
                if color_map is not None:
                    for cmap in color_map:
                        print (cmap)
                        if float(msg)>cmap:
                            color = color_map[cmap]
                            break
                
                if isinstance(widget, SegmentDisplay):
                    print ("segment")
                    # Map message to a value for a 7-segment display
                    widget.set_value(msg)
                elif isinstance(widget, StatusIndicator):
                    # Map message to a color for the status indicator
                    print ("indicator")
                    color = QColor(msg)
                    widget.set_color(color)
                elif isinstance(widget, TextDisplay):
                    # Update text for the TextDisplay widget
                    widget.set_color(color)
                    widget.set_text(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # MQTT parameters
    broker = MQTT_BROKER
    port = 1883
    
    topics = {"/out/state": [
                    {
                        'field': 'LF_SPORT_MOD_STATE.mode',
                        'widget': TextDisplay("Waiting..."),
                        'label': 'Dog State'
                    },
                    {
                        'field': 'LOW_STATE.bms_state.soc',
                        'widget': TextDisplay("Waiting..."),
                        'label': 'Battery (%)',
                        'color_map': {
                            75: 'green',
                            25: 'yellow',
                            0:  'red'
                        }
                    }
                ],
                "/out/mode": [
                    {
                        'field': None,
                        'widget': TextDisplay("Waiting for message..."),
                        'label': 'Dog Mode'
                    }
                ]
            }

    # Create the MQTT listener
    print ('Subscribing to...')
    print (list(topics.keys()))
    mqtt_listener = MqttListener(broker, port, list(topics.keys()))

    # Connect to MQTT broker
    mqtt_listener.connect_to_broker()
    print ('Connected')
    # # Create and show the PySide6 application window
    main_window = MainWindow(mqtt_listener, topics)
    main_window.show()

    # Start the Qt application event loop
    sys.exit(app.exec())