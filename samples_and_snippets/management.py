from datetime import datetime
import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage
import json

BROKER, PORT = "localhost", 1883


class Car:
    def __init__(self, license_plate: str = "ABC-123",
                 model: str = "2008 Hyundai",
                 entry_time=datetime.now().strftime('%H:%M:%S'),
                 exit_time=""):
        self.license_plate = license_plate
        self.model = model
        self.entry_time = entry_time
        self.exit_time = exit_time


class CarPark:
    def __init__(self, cars: list[Car], available_bays: int = 130):
        self.cars = cars
        self.available_bays = available_bays

    def get_available_bays(self):
        return self.available_bays

    def add_car(self, car: Car):
        # add a car to self.cars
        if self.available_bays > 0:
            self.cars.append(car)
            self.available_bays -= 1

    def remove_car(self, car: Car):
        if car in self.cars:
            self.cars.remove(car)
            self.available_bays += 1
            clear_blank_lines('car_park')

    @staticmethod
    def get_car_park():
        the_park: list[Car] = []
        with open('car_park', 'r') as park:
            for line in park:
                if line != "":
                    components = line.split(', ')
                    the_park.append(Car(components[0], components[1], components[2], ""))

            return the_park


class CarParkManagement:
    def __init__(self, car_park: CarPark):
        self.carpark = car_park
        self.client = paho.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT)
        self.client.loop_forever()

    def track_parking_bay(self, target_bay):
        count = 0
        for item in self.carpark.cars:
            count += 1
            if count == target_bay:
                if item == '':
                    print("The bay is empty.")
                else:
                    print("There is a " + item.model +
                          " with license plate " + item.license_plate +
                          " at bay " + target_bay)

    def write_log(self, message: str, file_path):
        with open(file_path, 'r') as logs:
            logs.write(message + '\n')

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print("Car Park Management Connected")
        client.subscribe("lot/sensor")

    def on_message(self, client, userdata, msg: MQTTMessage):
        payload = msg.payload.decode()
        print(payload)
        if 'exit' in payload:
            payload = payload[len("exit: "):]
            components = payload.split(', ')
            leaving_car = Car(components[0], components[1], components[2], "")
            self.carpark.remove_car(leaving_car)

            log_message = "A " + str(components[1]) +\
                          " with license plate " + str(components[0])\
                          + " has left at " + str(datetime.now().strftime('%H:%M:%S'))
            self.write_log(log_message, 'carpark_log')
        elif 'entry' in payload:
            payload = payload[len("entry: "):]
            components = payload.split(', ')
            new_car = Car(components[0], components[1], components[2], "")
            self.carpark.add_car(new_car)

            log_message = "A " + str(components[1]) + \
                          " with license plate " + str(components[0])\
                          + " has entered at " + str(datetime.now().strftime('%H:%M:%S'))
            self.write_log(log_message, 'carpark_log')


def clear_blank_lines(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Remove blank lines
    non_blank_lines = [line for line in lines if line.strip()]

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(non_blank_lines)


if __name__ == '__main__':
    the_cars: list[Car] = []
    clear_blank_lines('car_park')
    with open('car_park', 'r') as park:
        for line in park:
            if line != "":
                components = line.split(', ')
                new_car = Car(components[0], components[1], components[2], "")
                the_cars.append(new_car)

    with open('config.json', 'r') as file:
        data = json.load(file)
        count = data['CarParks'][0]['total-spaces']

    the_park = CarPark(the_cars, count)

    CarParkManagement(the_park)
