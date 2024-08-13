import time
import zmq
import json
import random
import threading

class VehicleSimulator:
    def __init__(self):
        self.context = zmq.Context()
        self.sender = self.context.socket(zmq.PUB)
        self.sender.bind("tcp://*:5555")
        
        self.receiver = self.context.socket(zmq.SUB)
        self.receiver.connect("tcp://localhost:5556")
        self.receiver.setsockopt_string(zmq.SUBSCRIBE, "")

        self.lev_status = False
        self.prop_status = False

    def simulate_levitation(self):
        base_height = 100
        while True:
            if self.lev_status:
                noise = random.uniform(-5, 5)
                height = base_height + noise
                return int(height)
            time.sleep(0.1)

    def simulate_propulsion(self):
        base_speed = 300
        while True:
            if self.prop_status:
                noise = random.uniform(-20, 20)
                speed = base_speed + noise
                return int(speed)
            time.sleep(0.1)

    def send_sensor_data(self):
        while True:
            lev_data = self.simulate_levitation() if self.lev_status else 0
            prop_data = self.simulate_propulsion() if self.prop_status else 0
            data = {
                "type": "sensor_data",
                "data": [lev_data, prop_data]
            }
            self.sender.send_string(json.dumps(data))
            time.sleep(0.1)

    def send_status_update(self):
        status = {
            "type": "status_update",
            "levitation": self.lev_status,
            "propulsion": self.prop_status
        }
        self.sender.send_string(json.dumps(status))

    def handle_commands(self):
        while True:
            try:
                message = self.receiver.recv_string(flags=zmq.NOBLOCK)
                command = json.loads(message)
                if command["type"] == "command":
                    if command["command"] == "start_levitation":
                        self.lev_status = True
                    elif command["command"] == "stop_levitation":
                        self.lev_status = False
                    elif command["command"] == "start_propulsion":
                        self.prop_status = True
                    elif command["command"] == "stop_propulsion":
                        self.prop_status = False
                    self.send_status_update()
            except zmq.Again:
                pass
            time.sleep(0.1)

    def run(self):
        threading.Thread(target=self.send_sensor_data, daemon=True).start()
        threading.Thread(target=self.handle_commands, daemon=True).start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Simulator terminated by user")
        finally:
            self.sender.close()
            self.receiver.close()
            self.context.term()

if __name__ == "__main__":
    simulator = VehicleSimulator()
    simulator.run()