from datetime import datetime

import mqtt_device
import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage
import json


class CarPark(mqtt_device.MqttDevice):
    """Creates a carpark object to store the state of cars in the lot"""

    def __init__(self, config):
        super().__init__(config)
        self.total_spaces = config['CarParks'][0]['total-spaces']
        self.total_cars = config['CarParks'][0]['total-cars']
        self.client.on_message = self.on_message
        self.client.subscribe('lot/sensor')
        self.client.loop_forever()
        self._temperature = None

    @property
    def available_spaces(self):
        available = self.total_spaces - self.total_cars
        return max(available, 0)

    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        
    def _publish_event(self):
        readable_time = datetime.now().strftime('%H:%M:%S')
        print(
            (
                f"TIME: {readable_time}, "
                + f"SPACES: {self.available_spaces}, "
                + "TEMPC: 42"
            )
        )
        message = (
            f"TIME: {readable_time}, "
            + f"SPACES: {self.available_spaces}, "
            + "TEMPC: 42"
        )
        self.client.publish('display', message)

    def on_car_entry(self):
        self.total_cars += 1
        self._publish_event()

    def on_car_exit(self):
        self.total_cars -= 1
        self._publish_event()

    def on_message(self, client, userdata, msg: MQTTMessage):
        payload = msg.payload.decode()
        print(payload)
        # TODO: Extract temperature from payload
        #obj = json.loads(payload)
        #self._temperature = obj[]
        if 'exit' in payload:
            self.on_car_exit()
        else:
            self.on_car_entry()
        with open('../samples_and_snippets/config.json', 'w') as file:
            json.dump(config, file)
            print(file)


if __name__ == '__main__':
    # TODO: Read config from file
    with open('../samples_and_snippets/config.json') as f:
        config = json.load(f)

    car_park = CarPark(config)
    print("Carpark initialized")
