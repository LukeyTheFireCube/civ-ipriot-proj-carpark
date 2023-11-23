import tkinter as tk
import paho.mqtt.client as paho
import json
import random
import string
from datetime import datetime
from management import Car

BROKER, PORT = "localhost", 1883


class CarDetector:
    """Provides a couple of simple buttons that can be used to represent a sensor detecting a car.
    This is a skeleton only."""

    def __init__(self):
        self.client = paho.Client()
        self.client.connect(BROKER, PORT)

        self.root = tk.Tk()
        self.root.title("Car Detector ULTRA")

        self.btn_incoming_car = tk.Button(
            self.root, text='🚘 Incoming Car', font=('Arial', 50),
            cursor='right_side', command=self.incoming_car)
        self.btn_incoming_car.pack(padx=10, pady=5)
        self.btn_outgoing_car = tk.Button(
            self.root, text='Outgoing Car 🚘',  font=('Arial', 50),
            cursor='bottom_left_corner', command=self.outgoing_car)
        self.btn_outgoing_car.pack(padx=10, pady=5)

        self.root.mainloop()

    @staticmethod
    def get_license_plate():
        count = 3
        car_plate = ""
        while count != 0:
            car_plate = car_plate + random.choice(string.ascii_letters)
            count -= 1
        count = 3
        car_plate = car_plate + "-"
        while count != 0:
            car_plate = car_plate + str(random.randint(0, 9))
            count -= 1

        return car_plate

    @staticmethod
    def get_car_model():
        with open('car_models', 'r') as models:
            car_models = models.read().splitlines()

            if car_models:
                return random.choice(car_models)
            else:
                return "ERR"

    @staticmethod
    def get_car_park():
        count = 0
        the_park: list[Car] = []
        with open('car_park', 'r') as park:
            for line in park:
                if line != "":
                    count += 1
                    components = line.split(', ')
                    the_park.append(Car(components[0], components[1], components[2], ""))

            return the_park, count

    def clear_target_line(self, file_path, target_line_number=1):
        # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Clear the target line
        if 1 <= target_line_number <= len(lines):
            lines[target_line_number - 1] = '\n'

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)

    def incoming_car(self):
        with open('config.json', 'r') as file:
            data = json.load(file)

        new_car = Car(self.get_license_plate(),
                      self.get_car_model(),
                      datetime.now().strftime('%H:%M:%S'),
                      "")
        message = "A " + new_car.model + " with license plate " + new_car.license_plate + " goes in."
        self.client.publish("lot/sensor", message)

        # TODO: implement this method to publish the detection via MQTT
        if data['CarParks'][0]['total-spaces'] > 0:
            message = new_car.license_plate +\
                      ", " + new_car.model +\
                      ", " + new_car.entry_time

            with open('car_park', 'a') as park:
                park.write(message + '\n')
            self.client.publish("lot/sensor",
                                "entry: " + message)

            data['CarParks'][0]['total-spaces'] -= 1
            data['CarParks'][0]['total-cars'] += 1
            with open('config.json', 'w') as file:
                json.dump(data, file)

        else:
            self.client.publish("lot/sensor",
                                "Car park is full.")

    def outgoing_car(self):
        with open('config.json', 'r') as file:
            data = json.load(file)

        park, number_of_cars = self.get_car_park()
        # TODO: implement this method to publish the detection via MQTT
        if data['CarParks'][0]['total-cars'] > 0 and number_of_cars > 0:
            leaving_car = park[0]
            message = "A " + leaving_car.model + " with license plate " + leaving_car.license_plate + " leaves."
            self.clear_target_line('car_park', 1)
            self.client.publish("lot/sensor", message)

            message = leaving_car.license_plate + \
                      ", " + leaving_car.model + \
                      ", " + datetime.now().strftime('%H:%M:%S')

            data['CarParks'][0]['total-spaces'] += 1
            data['CarParks'][0]['total-cars'] -= 1
            with open('config.json', 'w') as file:
                json.dump(data, file)

            self.client.publish("lot/sensor",
                                "exit: " + message)
        else:
            self.client.publish("lot/sensor",
                                "Car park is empty.")
