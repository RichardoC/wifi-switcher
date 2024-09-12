# wifi-switcher

For switching between multiple wifi networks on the Tildagon. This will not change your actual WiFi settings which will reset after a restart.

## How to set networks

When connected with mpremote, set the list of networks.

The networks must be a json of the following format. Leave username blank if it's not enterprise wifi.

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

### Commands using mpremote

This assumes you have connected to the device using [mpremote](https://tildagon.badge.emfcamp.org/using-the-badge/connect-to-wifi/#option-4-use-mpremote-to-edit-the-settings-file)

```python

import settings
settings.set("RichardoC_wifi_switcher", """[
    {
        "ssid": "abc",
        "password": "abc",
        "username": ""
    },
    {
        "ssid": "def",
        "password": "def",
        "username": "example"
    }
]""")

# confirm it was set correctly
import json
json.loads(settings.get("RichardoC_wifi_switcher"))

[
    {
        "ssid": "abc",
        "password": "abc",
        "username": ""
    },
    {
        "ssid": "def",
        "password": "def",
        "username": "example"
    }
]

# save the updated networks
settings.save()

```
