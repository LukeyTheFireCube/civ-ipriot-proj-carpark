import tkinter as tk
import paho.mqtt.client as paho
import json

BROKER, PORT = "localhost", 1883
class CarDetector:
    """Provides a couple of simple buttons that can be used to represent a sensor detecting a car.
    This is a skeleton only."""

    def __init__(self, data):
        self.data = data

        self.client = paho.Client()
        self.client.connect(BROKER, PORT)

        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50), cursor='right_side', command=self.incoming_car)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘',  font=('Arial', 50), cursor='bottom_left_corner', command=self.outgoing_car)
        self.btn_outgoing_car.pack(padx=10, pady=5)

        self.root.mainloop()

    def incoming_car(self):
        # TODO: implement this method to publish the detection via MQTT
        if self.data['CarParks'][0]['total-spaces'] > 0 and self.data['CarParks'][0]['total-cars'] < 130:
            self.data['CarParks'][0]['total-spaces'] -= 1
            self.data['CarParks'][0]['total-cars'] += 1
            with open('config.json', 'w') as file:
                json.dump(self.data, file)
            self.client.publish("lot/sensor", f"Car goes in. Bays remaining: {self.data['CarParks'][0]['total-spaces']}")
        else:
            self.client.publish("lot/sensor", f"Car park is full. Bays remaining: {self.data['CarParks'][0]['total-spaces']}")


    def outgoing_car(self):
        # TODO: implement this method to publish the detection via MQTT
        if self.data['CarParks'][0]['total-cars'] > 0:
            self.data['CarParks'][0]['total-spaces'] += 1
            self.data['CarParks'][0]['total-cars'] -= 1
            with open('config.json', 'w') as file:
                json.dump(self.data, file)

            # self.client.loop_start()
            self.client.publish("lot/sensor", f"Car goes out. Bays remaining: {self.data['CarParks'][0]['total-spaces']}")
            # self.client.loop_stop()
        else:
            # self.client.loop_start()
            self.client.publish("lot/sensor", f"Car park is empty. Bays remaining: {self.data['CarParks'][0]['total-spaces']}")
            # self.client.loop_stop()
