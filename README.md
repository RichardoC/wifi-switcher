# wifi-switcher

For switching between multiple wifi networks on the Tildagon. This will not change your actual WiFi settings which will reset after a restart.

## How to set networks

Edit the `/apps/RichardoC_wifi_switcher/networks.json` file on your device, once you've installed the app.

The format is as below. Leave username blank if it's not enterprise wifi.

```json
[
    {
        "ssid": "SOME_NETWORK",
        "password": "SOME_PASSWORD",
        "username": "SOME_ENTERPRISE_USERNAME"
    },
    {
        "ssid": "ANOTHER_NETWORK",
        "password": "ANOTHER PASSWORD",
        "username": ""
    }
]

```
