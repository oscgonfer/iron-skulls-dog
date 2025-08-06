import sys
import paho.mqtt.client as mqtt
from PySide6.QtCore import Signal, QObject, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout
from PySide6.QtGui import QColor, QPainter, QBrush
from config import *
import json
from tools import get_by_path

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
        # print(f"Received message on {topic}: {message}")
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
    def __init__(self, text="Waiting..."):
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
                if item['field'] is not None:
                    if '*' in item['field']:
                        _row = 0
                        for i in range(item['number']):
                            self.layout.addWidget(QLabel(f"{label}_{i}"), _row, 2)
                            _widg = widget()
                            _widg.setObjectName(f"{label}_{i}")
                            self.layout.addWidget(_widg, _row, 3)
                            _row += 1
                            # print (_widg)
                    else:
                        self.layout.addWidget(QLabel(label), row, 0)
                        _widg = widget()
                        _widg.setObjectName(label)
                        self.layout.addWidget(_widg, row, 1)
                        # print (_widg)
                else:
                    self.layout.addWidget(QLabel(label), row, 0)
                    _widg = widget()
                    _widg.setObjectName(label)
                    self.layout.addWidget(_widg, row, 1)
                    # print (_widg)
                row += 1

        self.mqtt_listener = mqtt_listener
        self.mqtt_listener.message_received.connect(self.update_display)

        # Set central widget
        central_widget = QWidget(self)
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.resize(400, 300)

    def update_widget(self, widget, msg, color):
        # print ('updating widget', widget, msg, color)
        if isinstance(widget, SegmentDisplay):
            # Map message to a value for a 7-segment display
            widget.set_value(msg)
        elif isinstance(widget, StatusIndicator):
            # Map message to a color for the status indicator
            color = QColor(msg)
            widget.set_color(color)
        elif isinstance(widget, TextDisplay):
            # Update text for the TextDisplay widget
            widget.set_color(color)
            widget.set_text(msg)

    def update_display(self, topic, message):
        """Update the display based on the MQTT topic and message"""
        # print(f"Updating display for {topic}: {message}")
        if topic in self.widgets:
            # widget = self.widgets[topic]
            for item in self.widgets[topic]:
                field = item['field']
                label = item['label']
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
                        if '*' in field:
                            msg = []
                            for item in get_by_path(js, field.split('.')):
                                msg.append(str(item))
                        else:
                            msg = str(get_by_path(js, field.split('.')))
                            # We have a float?
                            if '.' in msg:
                                if msg.lstrip("-").replace('.','',1).isdigit():
                                    msg = str(round(float(msg), 3))
                else: 
                    msg = message.strip("\"")
                                
                color = "white"
                if color_map is not None:
                    if type(msg) != list:
                        for cmap in color_map:
                            if type(cmap) == int:
                                if float(msg)>cmap:
                                    color = color_map[cmap]
                                    break
                            elif type(cmap) == str:
                                if cmap == msg:
                                    color = color_map[cmap]
                                    break
                        self.update_widget(self.findChild(QWidget, label), msg, color)
                    else:
                        i = 0
                        for _msg in msg:
                            # print ('msg', _msg, f"{label}_{i}")
                            for cmap in color_map:
                                if type(cmap) == int:
                                    if float(_msg)>cmap:
                                        color = color_map[cmap]
                                        break
                                elif type(cmap) == str:
                                    if cmap == _msg:
                                        color = color_map[cmap]
                                        break
                            # print (color)
                            self.update_widget(self.findChild(QWidget, f"{label}_{i}"), _msg, color)
                            i += 1
                else:
                    self.update_widget(self.findChild(QWidget, label), msg, color)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # MQTT parameters
    broker = MQTT_BROKER
    port = 1883
    
    topics = {
                "/out/mode/mode": [
                    {
                        'field': None,
                        'widget': TextDisplay,
                        'label': 'Dog Mode',
                        'color_map': {
                            "normal": 'green',
                            "advanced": 'purple',
                            "ai":  '#0055FF'
                        }
                    }
                ],
                "/out/mpc": [
                    {
                        'field': "FADER_5.input_state",
                        'widget': TextDisplay,
                        'label': 'Velocidad horizontal',
                        'color_map': {
                            100: 'red',
                            60: 'yellow',
                            0:  'green'
                        }
                    },
                    {
                        'field': "FADER_6.input_state",
                        'widget': TextDisplay,
                        'label': 'Velocidad giro',
                        'color_map': {
                            100: 'red',
                            60: 'yellow',
                            0:  'green'
                        }
                    },
                    {
                        'field': "FADER_7.input_state",
                        'widget': TextDisplay,
                        'label': 'Velocidad gesto',
                        'color_map': {
                            100: 'red',
                            60: 'yellow',
                            0:  'green'
                        }
                    }
                ],
                "/out/state/LF_SPORT_MOD_STATE": [
                    {
                        'field': 'LF_SPORT_MOD_STATE.mode',
                        'widget': TextDisplay,
                        'label': 'Dog State'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.bodyHeight',
                        'widget': TextDisplay,
                        'label': 'Body Height'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.brightness',
                        'widget': TextDisplay,
                        'label': 'Led Brightness'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.footRaiseHeight',
                        'widget': TextDisplay,
                        'label': 'Foot Raise Height'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.obstaclesAvoidSwitch',
                        'widget': TextDisplay,
                        'label': 'Obstacle Avoid Switch'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.speedLevel',
                        'widget': TextDisplay,
                        'label': 'Speed Level'
                    },
                    {
                        'field': 'LF_SPORT_MOD_STATE.volume',
                        'widget': TextDisplay,
                        'label': 'Volume'
                    },
                    {
                        'field': 'LOW_STATE.bms_state.soc',
                        'widget': TextDisplay,
                        'label': 'Battery (%)',
                        'color_map': {
                            75: 'green',
                            25: 'yellow',
                            0:  'red'
                        }
                    },
                    {
                        'field': 'LOW_STATE.motor_state.*.temperature',
                        'widget': TextDisplay,
                        'label': 'Temperature (degC)',
                        'color_map': {
                            80: 'red',
                            60: 'yellow',
                            30:  'green'
                        },
                        'number': 12
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