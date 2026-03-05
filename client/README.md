# UKW client

A MicroPython client for the Waveshare ESP32-S3 that polls the UKW server's `/status/monitors` endpoint and shows aggregate status on the board's RGB LED (WS2812/NeoPixel).

| LED colour | Meaning |
|------------|---------------------------------------------|
| Green | All monitors are up |
| Red | One or more monitors are down |
| Blue | Polling / connecting to WiFi |
| Yellow | Error (server unreachable, bad response) |

## Hardware

Waveshare ESP32-S3 1.47inch LCD Display Development Board, 172×320, 262K Color, Dual-Core Processor Up to 240MHz Frequency, Supports WiFi & BLE 5, with Colorful RGB LED

## Software

MicroPython — see https://docs.waveshare.com/ESP32-S3-Zero/Development-Environment-Setup-MicroPython

## Setup

1. Flash MicroPython onto the board (see link above).
2. Copy `config.py` and `main.py` to the board (e.g. via `mpremote` or Thonny).
3. Edit `config.py` with your WiFi credentials and UKW server URL:

```python
WIFI_SSID = "your-ssid"
WIFI_PASSWORD = "your-password"
UKW_SERVER_URL = "http://192.168.1.100:5000"
LED_PIN = 21        # GPIO pin for the WS2812 RGB LED
POLL_INTERVAL = 30  # seconds between polls
```

4. Reset the board — `main.py` runs automatically on boot.