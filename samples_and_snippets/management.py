import random
from datetime import datetime
import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage

BROKER, PORT = "localhost", 1883

class Car:
    def __init__(self, license_plate: str,
                 entry_time=datetime.now().strftime('%H:%M:%S'),
                 exit_time=datetime.now().strftime('%H:%M:%S')):
        self.license_plate = license_plate
        self.entry_time = entry_time
        self.exit_time = exit_time


class CarPark:
    def __init__(self, cars: list[Car], total_bays: int = 100):
        self.cars = cars
        self.total_bays = total_bays

    def add_car(self, car: Car):
        # add a car to self.cars
        self.cars.append(car)

    def remove_car(self, car: Car):
        if car in self.cars:
            self.cars.remove(car)

    @property
    def temperature(self):
        return random.randint(19, 22)


class CarParkManagement:
    def __init__(self, car_parks: list[CarPark]):
        self.carparks = [car_parks]
        self.client = paho.Client()
        self.client.connect(BROKER, PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print("Car Park Display Connected")
        client.subscribe("lot/sensor")

    def on_message(self, client, userdata, msg: MQTTMessage):
        payload = msg.payload.decode()
        if 'exit' in payload:
            CarPark.remove_car()
        else:
            CarPark.add_car()