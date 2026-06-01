import app

from app_components import Menu, Notification, clear_background
from events.input import Buttons

import json
import settings
import wifi

SETTINGS_PATH = "RichardoC_wifi_switcher"
main_menu_items = ["Network List"]

class WifiSwitcherApp(app.App):
    buttons: Buttons
    networks: []
    notification: Notification

    def __init__(self):
        self.menu = None
        ## Discover existing wifi networks from file
        self.button_states = Buttons(self)
        self.networks = []
        

        stored_networks = settings.get(SETTINGS_PATH)
        if stored_networks is None:
            self.notification = Notification(f'No networks present in {SETTINGS_PATH}, please add some')
            self.button_states.clear()
            self.minimise()
            return

        try:
            self.networks = json.loads(stored_networks)
            # Replace empty strings with None
            # This is to match what the connect call is expecting
            for item in self.networks:
                for key, value in item.items():
                    if value == "":
                        item[key] = None
                
        except Exception as e:
            self.notification = Notification(f'Failed to read networks.json file with error {e}')
            import time
            time.sleep(5)
            self.button_states.clear()
            self.minimise()

        for network in self.networks:
            main_menu_items.append(network["ssid"])
            
        # Create the menu object
        print("Making menu object with the following contents...")
        print(main_menu_items)
        self.menu = Menu(
            self,
            main_menu_items,
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )
        self.notification = None


    def select_handler(self, item, position):
        ## Connect to that wifi
        ## Then show notification
        if position == 0:
            self.notification = Notification(f'Not a network, please select a network')
            return
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
        if self.menu:
            self.menu.update(delta)
        if self.notification:
            self.notification.update(delta)


    def draw(self, ctx):
        clear_background(ctx)
        # Display the menu on the device
        # as a scrollable list of wifi networks
        if self.menu:
            self.menu.draw(ctx)
        if self.notification:
            self.notification.draw(ctx)

__app_export__ = WifiSwitcherApp

