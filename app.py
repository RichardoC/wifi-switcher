import app

from app_components import (
    Menu,
    Notification,
    label_font_size,
    small_font_size,
    set_color,
)
from app_components.background import Background
from events.input import Buttons, BUTTON_TYPES, ButtonDownEvent
from system.eventbus import eventbus

import asyncio
import json
import network
import settings
import wifi

SETTINGS_PATH = "RichardoC_wifi_switcher"
main_menu_items = []


def wrap_text(ctx, text, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if not current or ctx.text_width(candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class WifiSwitcherApp(app.App):
    buttons: Buttons
    networks: []
    notification: Notification

    def __init__(self):
        self.menu = None
        self.needs_setup = False
        ## Discover existing wifi networks from file
        self.button_states = Buttons(self)
        self.networks = []

        stored_networks = settings.get(SETTINGS_PATH)
        if stored_networks is None:
            self.notification = None
            self.needs_setup = True
            eventbus.on_async(ButtonDownEvent, self._handle_buttondown, self)
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
            self.notification = Notification(
                f"Invalid {SETTINGS_PATH} setting ({e}), see README to fix"
            )
            import time

            time.sleep(5)
            self.button_states.clear()
            self.minimise()
            return

        main_menu_items.clear()
        for net in self.networks:
            main_menu_items.append(net["ssid"])

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
        # Show a notification straight away, then connect in the background
        # so the notification actually gets a chance to be drawn
        net = self.networks[position]
        ssid = net["ssid"]
        self.notification = Notification(f"Connecting to {ssid}...")
        asyncio.create_task(self._connect(net))

    async def _connect(self, net):
        # Connect to that wifi, wait to see if it actually worked, then show
        # the real outcome (also on stdout, for debug)
        ssid = net["ssid"]
        try:
            print(f"wifi-switcher: connecting to {ssid}")
            # Force a real disconnect first - otherwise a failed attempt to
            # join a new ssid can just leave the previous connection in place
            wifi.disconnect()
            wifi.connect(ssid, net["password"], net.get("username"))
            await wifi.async_wait()
            sta_status = wifi.get_sta_status()
            if sta_status == network.STAT_GOT_IP:
                print(f"wifi-switcher: connected to {ssid}, ip={wifi.get_ip()}")
                self.notification = Notification(f"Connected to {ssid}")
            else:
                print(
                    f"wifi-switcher: failed to connect to {ssid}, status={sta_status}"
                )
                self.notification = Notification(f"Failed to connect to {ssid}")
        except Exception as e:
            print(f"wifi-switcher: failed to connect: {e}")
            self.notification = Notification(f"Failed to connect to network: {e}")

    def back_handler(self):
        self.button_states.clear()
        self.minimise()

    async def _handle_buttondown(self, event):
        if BUTTON_TYPES["CANCEL"] in event.button:
            self.back_handler()

    def update(self, delta):
        if self.menu:
            self.menu.update(delta)
        if self.notification:
            self.notification.update(delta)

    def draw(self, ctx):
        Background.draw(ctx)
        # Display the menu on the device
        # as a scrollable list of wifi networks
        if self.menu:
            ctx.save()
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            set_color(ctx, "yellow")
            header = "Network List"
            ctx.font_size = small_font_size
            # Screen is round, so the safe text width shrinks near the top edge
            header_max_width = 110
            header_width = ctx.text_width(header)
            if header_width > header_max_width:
                ctx.font_size = small_font_size * header_max_width / header_width
            ctx.move_to(0, -85).text(header)
            ctx.restore()
            self.menu.draw(ctx)
        elif self.needs_setup:
            ctx.save()
            ctx.font_size = small_font_size
            ctx.text_align = ctx.CENTER
            ctx.text_baseline = ctx.MIDDLE
            set_color(ctx, "label")
            # Screen is round, so keep wrapped lines within a safe central width
            lines = wrap_text(ctx, "No networks configured", 160)
            lines += wrap_text(ctx, "See README for setup instructions", 160)
            line_height = small_font_size * 1.4
            y = -(len(lines) - 1) * line_height / 2
            for line in lines:
                ctx.move_to(0, y).text(line)
                y += line_height
            ctx.restore()
        if self.notification:
            self.notification.draw(ctx)


__app_export__ = WifiSwitcherApp
