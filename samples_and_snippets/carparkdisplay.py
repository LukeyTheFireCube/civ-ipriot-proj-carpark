import random
import time
import threading
import tkinter as tk
from typing import Iterable
import json

import paho.mqtt.client as paho
# from paho.mqtt.client import MQTTMessage

BROKER, PORT = "localhost", 1883


class WindowedDisplay:
    """Displays values for a given set of fields as a simple GUI window.
    Use .show() to display the window; use .update() to update the values displayed.
    """

    DISPLAY_INIT = '– – –'
    SEP = ':'  # field name separator

    def __init__(self, title: str, display_fields: Iterable[str]):
        """Creates a Windowed (tkinter) display to replace sense_hat display.
        To show the display (blocking) call .show() on the returned object.

        Parameters
        ----------
        title : str
            The title of the window (usually the name of your car park from the config)
        display_fields : Iterable
            An iterable (usually a list) of field names for the UI.
            Updates to values must be presented in a dictionary with these values as keys.
        """
        self.window = tk.Tk()
        self.window.title(f'{title}: Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):

            # create the elements
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field+self.SEP, font=('Arial', 50))
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            # position the elements
            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=2, sticky=tk.W, padx=10)

    def show(self):
        """Display the GUI. Blocking call."""
        self.window.mainloop()

    def update(self, updated_values: dict):
        """Update the values displayed in the GUI.
        Expects a dictionary with keys matching the field names passed to the constructor."""
        for field in self.gui_elements:
            if field.startswith('lbl_field'):
                field_value = field.replace('field', 'value')
                self.gui_elements[field_value].configure(
                    text=updated_values[self.gui_elements[field].cget('text').rstrip(self.SEP)])
        self.window.update()


class CarParkDisplay:
    """Provides a simple display of the car park status.
    This is a skeleton only.
    The class is designed to be customizable without requiring and understanding of tkinter or threading."""
    # determines what fields appear in the UI
    fields = ['Available bays', 'Temperature', 'At']

    def __init__(self):
        self.client = paho.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.connect(BROKER, PORT)
        self.window = WindowedDisplay(
            'Moondalup', CarParkDisplay.fields)
        updater = threading.Thread(target=self.check_updates)
        updater.daemon = True
        updater.start()
        self.window.show()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print("Car Park Display Connected")
        client.subscribe("lot/sensor")

    def on_message(self, client, userdata, msg):
        print(f'Received {msg.payload}')
        # When you get an update, refresh the display.
        the_fields = self.get_field_values()
        self.window.update(the_fields)

    @staticmethod
    def get_field_values():
        with open('config.json') as file:
            data = json.load(file)

            available_bays = data['CarParks'][0]['total-spaces']

        field_values = dict(zip(CarParkDisplay.fields, [
            f'{available_bays:03d}',
            f'{random.randint(19, 22):02d}℃',
            time.strftime("%H:%M:%S")]))
        return field_values

    def check_updates(self):
        # TODO: This is where you should manage the MQTT subscription

        while True:
            # NOTE: Dictionary keys *must* be the same as the class fields
            the_fields = self.get_field_values()
            # Pretending to wait on updates from MQTT
            self.window.update(the_fields)
            self.client.loop_forever()


