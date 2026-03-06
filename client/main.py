"""
UKW Client for Waveshare ESP32-S3 1.47inch LCD Development Board

Polls the UKW server's /status/monitors endpoint and displays the
aggregate status on the board's RGB LED (WS2812/NeoPixel):

  - Green : all monitors are up
  - Red   : one or more monitors are down
  - Blue  : polling / connecting
  - Yellow: error (server unreachable, bad response, etc.)
"""

import machine
import network
import neopixel
import urequests
import ujson
import time

from config import WIFI_SSID, WIFI_PASSWORD, UKW_SERVER_URL, LED_PIN, POLL_INTERVAL

# --- LED helpers ----------------------------------------------------------

led = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)

COLOR_OFF    = (0, 0, 0)
COLOR_GREEN  = (255, 128, 0)
COLOR_RED    = (255, 0, 0)
COLOR_BLUE   = (0, 0, 255)
COLOR_YELLOW = (255, 150, 0)
# COLOR_CYAN   = (0, 255, 255)
# COLOR_PURPLE = (180, 0, 255)

def set_led(color):
    led[0] = color
    led.write()


# --- WiFi -----------------------------------------------------------------

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("WiFi already connected:", wlan.ifconfig())
        return wlan

    print("Connecting to WiFi", WIFI_SSID, "...")
    set_led(COLOR_BLUE)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    retries = 0
    while not wlan.isconnected():
        retries += 1
        if retries > 30:
            print("WiFi connection failed")
            set_led(COLOR_YELLOW)
            return None
        time.sleep(1)

    print("WiFi connected:", wlan.ifconfig())
    return wlan


# --- Monitor polling ------------------------------------------------------

def poll_monitors():
    """Fetch /status/monitors and return True if all are up, False otherwise.
    Raises on network/parse errors."""
    url = UKW_SERVER_URL.rstrip("/") + "/status/monitors"
    response = urequests.get(url)

    try:
        if response.status_code != 200:
            raise RuntimeError("HTTP {}".format(response.status_code))

        monitors = ujson.loads(response.text)

        if not monitors:
            raise RuntimeError("Empty monitor list")

        all_up = all(status == "up" for status in monitors.values())
        print("Monitors:", monitors, "-> all up" if all_up else "-> NOT all up")
        return all_up
    finally:
        response.close()


# --- Main loop ------------------------------------------------------------

def main():
    print("UKW Client starting")

    wlan = connect_wifi()
    if wlan is None:
        print("Retrying WiFi in 10 s ...")
        time.sleep(10)
        machine.reset()

    while True:
        set_led(COLOR_BLUE)
        try:
            if poll_monitors():
                set_led(COLOR_GREEN)
            else:
                set_led(COLOR_RED)
        except Exception as e:
            print("Error polling monitors:", e)
            set_led(COLOR_YELLOW)

        time.sleep(POLL_INTERVAL)


main()
