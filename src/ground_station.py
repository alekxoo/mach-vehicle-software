import sys
import zmq
import json
import time
from collections import deque
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
import pyqtgraph as pg
import numpy as np

class GroundStationSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ground Station Simulator")
        self.setGeometry(100, 100, 1000, 700)

        # ZMQ setup
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.SUB)
        self.receiver.connect("tcp://localhost:5555")
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        
        self.sender = self.context.socket(zmq.PUB)
        self.sender.bind("tcp://*:5556")

        # Data storage
        self.max_points = 1000
        self.lev_data = np.full(self.max_points, np.nan)
        self.prop_data = np.full(self.max_points, np.nan)
        self.time_data = np.linspace(0, -100, self.max_points)  # Last 100 seconds
        self.start_time = time.time()

        # System status
        self.lev_status = False
        self.prop_status = False

        # UI setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Plots
        self.plot_layout = QVBoxLayout()
        self.layout.addLayout(self.plot_layout)

        # Levitation plot
        self.lev_plot_widget = pg.PlotWidget()
        self.plot_layout.addWidget(self.lev_plot_widget)
        self.lev_curve = self.lev_plot_widget.plot(pen='r')
        self.lev_plot_widget.setLabel('left', 'Height (mm)')
        self.lev_plot_widget.setLabel('bottom', 'Time (s)')
        self.lev_plot_widget.setTitle('Levitation Height')

        # Propulsion plot
        self.prop_plot_widget = pg.PlotWidget()
        self.plot_layout.addWidget(self.prop_plot_widget)
        self.prop_curve = self.prop_plot_widget.plot(pen='b')
        self.prop_plot_widget.setLabel('left', 'Speed (dm/s)')
        self.prop_plot_widget.setLabel('bottom', 'Time (s)')
        self.prop_plot_widget.setTitle('Propulsion Speed')

        # Labels for current values and status
        self.lev_label = QLabel("Levitation Height: N/A")
        self.prop_label = QLabel("Propulsion Speed: N/A")
        self.lev_status_label = QLabel("Levitation Status: OFF")
        self.prop_status_label = QLabel("Propulsion Status: OFF")
        self.layout.addWidget(self.lev_label)
        self.layout.addWidget(self.lev_status_label)
        self.layout.addWidget(self.prop_label)
        self.layout.addWidget(self.prop_status_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.lev_start_button = QPushButton("Start Levitation")
        self.lev_stop_button = QPushButton("Stop Levitation")
        self.prop_start_button = QPushButton("Start Propulsion")
        self.prop_stop_button = QPushButton("Stop Propulsion")
        button_layout.addWidget(self.lev_start_button)
        button_layout.addWidget(self.lev_stop_button)
        button_layout.addWidget(self.prop_start_button)
        button_layout.addWidget(self.prop_stop_button)
        self.layout.addLayout(button_layout)

        # Connect buttons to functions
        self.lev_start_button.clicked.connect(lambda: self.send_command("start_levitation"))
        self.lev_stop_button.clicked.connect(lambda: self.send_command("stop_levitation"))
        self.prop_start_button.clicked.connect(lambda: self.send_command("start_propulsion"))
        self.prop_stop_button.clicked.connect(lambda: self.send_command("stop_propulsion"))

        # Timer for updating data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Update every 100 ms

    def receive_data(self):
        try:
            message = self.receiver.recv_string(flags=zmq.NOBLOCK)
            data = json.loads(message)
            print(f"Received from vehicle: {data}")
            return data
        except zmq.Again:
            return None

    def send_command(self, command):
        message = json.dumps({"type": "command", "command": command})
        self.sender.send_string(message)
        print(f"Sent command to vehicle: {message}")

    def update_data(self):
        data = self.receive_data()
        if data:
            if data["type"] == "sensor_data":
                lev_data, prop_data = data["data"]
                current_time = time.time() - self.start_time

                # Shift data
                self.lev_data = np.roll(self.lev_data, -1)
                self.prop_data = np.roll(self.prop_data, -1)
                self.time_data = np.roll(self.time_data, -1)

                # Update latest data point
                self.time_data[-1] = current_time
                self.lev_data[-1] = lev_data if self.lev_status else np.nan
                self.prop_data[-1] = prop_data if self.prop_status else np.nan

                # Update labels
                self.lev_label.setText(f"Levitation Height: {lev_data if self.lev_status else 'N/A'} mm")
                self.prop_label.setText(f"Propulsion Speed: {prop_data if self.prop_status else 'N/A'} dm/s")

                # Update plots
                self.lev_curve.setData(x=self.time_data, y=self.lev_data)
                self.prop_curve.setData(x=self.time_data, y=self.prop_data)

            elif data["type"] == "status_update":
                self.lev_status = data["levitation"]
                self.prop_status = data["propulsion"]
                self.update_status_labels()

    def update_status_labels(self):
        self.lev_status_label.setText(f"Levitation Status: {'ON' if self.lev_status else 'OFF'}")
        self.lev_status_label.setStyleSheet(f"color: {'green' if self.lev_status else 'red'}")
        self.prop_status_label.setText(f"Propulsion Status: {'ON' if self.prop_status else 'OFF'}")
        self.prop_status_label.setStyleSheet(f"color: {'green' if self.prop_status else 'red'}")

    def closeEvent(self, event):
        self.sender.close()
        self.receiver.close()
        self.context.term()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ground_station = GroundStationSimulator()
    ground_station.show()
    sys.exit(app.exec_())