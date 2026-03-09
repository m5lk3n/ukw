# UKW client

A MicroPython client for the Waveshare ESP32-S3 1.47" LCD board that polls the UKW server's `/status/monitors` endpoint and displays each monitor's up/down status on the 172×320 LCD screen.

The RGB LED also shows the aggregate status at a glance:

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

## Files

| File | Purpose |
|---------------|----------------------------------------------|
| `config.py` | WiFi, server URL, LCD & LED pin settings |
| `main.py` | Main client loop, WiFi, display rendering |
| `st7789.py` | Minimal ST7789 LCD driver (SPI, no framebuf) |

## Setup

1. Flash MicroPython onto the board (see link above).
2. Copy `config.py`, `st7789.py`, and `main.py` to the board (e.g. via `mpremote` or Thonny).
3. Edit `config.py` with your WiFi credentials and UKW server URL:

```python
WIFI_SSID = "your-ssid"
WIFI_PASSWORD = "your-password"
UKW_SERVER_URL = "http://192.168.1.100:5000"
POLL_INTERVAL = 30  # seconds between polls
```

   Verify the LCD GPIO pins match your board revision (defaults are for the standard Waveshare ESP32-S3-LCD-1.47).

4. Reset the board — `main.py` runs automatically on boot and the LCD will display each monitor with a green/red status indicator.