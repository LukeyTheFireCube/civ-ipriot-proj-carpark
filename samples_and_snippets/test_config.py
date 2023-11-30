import unittest
from unittest.mock import patch
from datetime import datetime

import json  # you can use toml, json,yaml, or ryo for your config file

from management import Car, CarPark
from cardetector import CarDetector


class TestConfigParsing(unittest.TestCase):
    def test_add_car(self):
        the_cars: list[Car] = []
        with open('car_park', 'r') as park:
            for line in park:
                if line != "":
                    components = line.split(', ')
                    new_car = Car(components[0], components[1], components[2], "")
                    the_cars.append(new_car)

        with open('config.json', 'r') as file:
            data = json.load(file)
            count = data['CarParks'][0]['total-spaces']
        carpark = CarPark(the_cars, count)

        dummy_car = Car("ABC-123", "2008 Hyundai", datetime.now().strftime('%H:%M:%S'), "")
        carpark.add_car(dummy_car)

        self.assertIn(dummy_car, carpark.cars)

        self.assertEqual(carpark.available_bays, count - 1)

    @patch('cardetector.paho.Client')
    @patch('cardetector.json.load')
    @patch('cardetector.json.dump')
    @patch('cardetector.open')
    def test_incoming_car(self, mock_open, mock_dump, mock_load, mock_paho):
        # NOTE: Due to the CarDetector class being blocking, the test case will never actually finish.
        # To undo this, comment out the main_loop in the CarDetector class.

        mock_data = {'CarParks': [{'total-spaces': 1, 'total-cars': 0}]}
        mock_load.return_value = mock_data
        mock_open.return_value.__enter__.return_value = mock_open
        mock_open.read.return_value = '{"CarParks": [{"total-spaces": 1, "total-cars": 0}]}'

        car_detector = CarDetector()

        mock_license_plate = 'ABC-123'
        mock_car_model = 'Test Model'
        mock_datetime_now = datetime.now().strftime('%H:%M:%S')
        with patch.object(car_detector, 'get_license_plate', return_value=mock_license_plate):
            with patch.object(car_detector, 'get_car_model', return_value=mock_car_model):
                car_detector.incoming_car()

        self.assertEqual(mock_data['CarParks'][0]['total-spaces'], 0)
        self.assertEqual(mock_data['CarParks'][0]['total-cars'], 1)
        mock_open.assert_called_with('config.json', 'w')
        mock_dump.assert_called_with(mock_data, mock_open)
        mock_paho().publish.assert_called_with('lot/sensor',
                                               f'entry: {mock_license_plate}, {mock_car_model}, {mock_datetime_now}')


if __name__ == '__main__':
    unittest.main()
