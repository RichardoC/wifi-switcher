import app

from app_components import Menu, Notification, clear_background
from events.input import Buttons

import json
import wifi


class WifiSwitcherApp(app.App):
    networks: object
    

    def __init__(self):
        ## Discover existing wifi networks from file
        self.button_states = Buttons(self)
        self.networks = []
        self.notification = Notification(f'Initialising')
        print("initialising")
        try:
            with open("/apps/RichardoC_wifi_switcher/networks.json", "r") as f:
                self.networks = json.load(f)
                # Replace empty strings with None
                # This is to match what the connect call is expecting
                for item in self.networks:
                    for key, value in item.items():
                        if value == "":
                            item[key] = None
                
        except Exception as e:
            self.networks = []
            self.notification = Notification(f'Failed to read networks.json file with error {e}')
            self.minimise()

        main_menu_items = ["Network List"]
        for network in self.networks:
            main_menu_items.append(network["ssid"])
        # Create the menu object
        self.menu = Menu(
            self,
            main_menu_items,
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )


    def select_handler(self, item, position):
        ## Connect to that wifi
        ## Then show notification
        try:
            network = self.networks[position -1]
            wifi.connect(network["ssid"], network["password"], network["username"])
        except Exception as e:
            self.notification = Notification(f'Failed to connect to network: {e}')
        

        self.notification = Notification('Connected to ' + self.networks[position -1]["ssid"])

    def back_handler(self):
        self.button_states.clear()
        self.minimise()

    def update(self, delta):
        self.menu.update(delta)
        if self.notification:
            self.notification.update(delta)


    def draw(self, ctx):
        clear_background(ctx)
        # Display the menu on the device
        # as a scrollable list of film titles
        self.menu.draw(ctx)
        if self.notification:
            self.notification.draw(ctx)

__app_export__ = WifiSwitcherApp