"""
UKW Client for Waveshare ESP32-S3 1.47inch LCD Development Board

Polls the UKW server's /status/monitors endpoint and displays each
monitor's up/down status on the 172×320 LCD screen.

The RGB LED still shows the aggregate status:
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

from config import (
    WIFI_SSID, WIFI_PASSWORD, UKW_SERVER_URL,
    LED_PIN, POLL_INTERVAL,
    LCD_DC_PIN, LCD_CS_PIN, LCD_CLK_PIN, LCD_DIN_PIN,
    LCD_RST_PIN, LCD_BL_PIN, LCD_SPI_ID, LCD_SPI_FREQ,
    LCD_ROTATION, FONT_SCALE,
)
from st7789 import ST7789, rgb565


# --- Colours (RGB565) -----------------------------------------------------

C_BLACK   = rgb565(0, 0, 0)
C_WHITE   = rgb565(255, 255, 255)
C_GREEN   = rgb565(0, 200, 0)
C_RED     = rgb565(220, 0, 0)
C_BLUE    = rgb565(40, 80, 220)
C_YELLOW  = rgb565(220, 180, 0)
C_GREY    = rgb565(60, 60, 60)
C_DKGREEN = rgb565(0, 40, 0)
C_DKRED   = rgb565(50, 0, 0)


# --- LED helpers -----------------------------------------------------------

led = neopixel.NeoPixel(machine.Pin(LED_PIN), 1)

LED_OFF    = (0, 0, 0)
LED_GREEN  = (0, 20, 0)
LED_RED    = (20, 0, 0)
LED_BLUE   = (0, 0, 20)
LED_YELLOW = (20, 12, 0)


def set_led(color):
    led[0] = color
    led.write()


# --- LCD setup -------------------------------------------------------------

spi = machine.SPI(
    LCD_SPI_ID,
    baudrate=LCD_SPI_FREQ,
    polarity=0,
    phase=0,
    sck=machine.Pin(LCD_CLK_PIN),
    mosi=machine.Pin(LCD_DIN_PIN),
)

lcd = ST7789(
    spi,
    dc=machine.Pin(LCD_DC_PIN, machine.Pin.OUT),
    cs=machine.Pin(LCD_CS_PIN, machine.Pin.OUT),
    rst=machine.Pin(LCD_RST_PIN, machine.Pin.OUT),
    bl=machine.Pin(LCD_BL_PIN, machine.Pin.OUT),
    rotation=LCD_ROTATION,
)


# --- Display helpers -------------------------------------------------------

CHAR_W = 8 * FONT_SCALE
CHAR_H = 8 * FONT_SCALE
PADDING = 4
ROW_H  = CHAR_H + PADDING * 2
HEADER_H = ROW_H + 2  # extra spacing below header


def show_message(text, fg=C_WHITE, bg=C_BLACK):
    """Show a single centred message on screen."""
    lcd.fill(bg)
    x = max(0, (lcd.width - len(text) * CHAR_W) // 2)
    y = lcd.height // 2 - CHAR_H // 2
    lcd.text(text, x, y, fg, bg, FONT_SCALE)


def draw_header():
    """Draw the title bar."""
    lcd.fill_rect(0, 0, lcd.width, HEADER_H, C_GREY)
    title = "UKW Monitors"
    x = max(0, (lcd.width - len(title) * CHAR_W) // 2)
    lcd.text(title, x, PADDING, C_WHITE, C_GREY, FONT_SCALE)


def draw_monitors(monitors):
    """Draw the full monitor list on screen.

    *monitors* is a dict  {name: "up"|"down", ...}
    """
    lcd.fill(C_BLACK)
    draw_header()

    y = HEADER_H + PADDING
    max_name_chars = (lcd.width - CHAR_W * 4 - PADDING * 3) // CHAR_W  # room for " UP" / " DN"

    for name, status in sorted(monitors.items()):
        if y + ROW_H > lcd.height:
            # Out of space — draw an ellipsis row
            lcd.text("...", PADDING, y + PADDING, C_WHITE, C_BLACK, FONT_SCALE)
            break

        is_up = status == "up"
        row_bg = C_DKGREEN if is_up else C_DKRED

        # Row background
        lcd.fill_rect(0, y, lcd.width, ROW_H, row_bg)

        # Status indicator dot
        dot_x = PADDING
        dot_color = C_GREEN if is_up else C_RED
        dot_size = CHAR_H
        lcd.fill_rect(dot_x, y + PADDING, dot_size, dot_size, dot_color)

        # Monitor name (truncated if needed)
        display_name = name[:max_name_chars] if len(name) > max_name_chars else name
        lcd.text(display_name, dot_x + dot_size + PADDING, y + PADDING, C_WHITE, row_bg, FONT_SCALE)

        # Status label on right
        label = "UP" if is_up else "DN"
        label_x = lcd.width - len(label) * CHAR_W - PADDING
        lcd.text(label, label_x, y + PADDING, C_GREEN if is_up else C_RED, row_bg, FONT_SCALE)

        y += ROW_H + 1  # 1px gap between rows

    # Summary line at bottom
    up_count = sum(1 for s in monitors.values() if s == "up")
    total = len(monitors)
    summary = "{}/{} up".format(up_count, total)
    sy = lcd.height - CHAR_H - PADDING
    lcd.fill_rect(0, sy - PADDING, lcd.width, CHAR_H + PADDING * 2, C_GREY)
    sx = max(0, (lcd.width - len(summary) * CHAR_W) // 2)
    color = C_GREEN if up_count == total else C_RED
    lcd.text(summary, sx, sy, color, C_GREY, FONT_SCALE)


# --- WiFi ------------------------------------------------------------------

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        print("WiFi already connected:", wlan.ifconfig())
        return wlan

    print("Connecting to WiFi", WIFI_SSID, "...")
    set_led(LED_BLUE)
    show_message("WiFi ...", C_BLUE)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    retries = 0
    while not wlan.isconnected():
        retries += 1
        if retries > 30:
            print("WiFi connection failed")
            set_led(LED_YELLOW)
            show_message("WiFi FAIL", C_RED)
            return None
        time.sleep(1)

    print("WiFi connected:", wlan.ifconfig())
    show_message("WiFi OK", C_GREEN)
    time.sleep(1)
    return wlan


# --- Monitor polling -------------------------------------------------------

def poll_monitors():
    """Fetch /status/monitors and return the dict {name: status}.
    Raises on network/parse errors."""
    url = UKW_SERVER_URL.rstrip("/") + "/status/monitors"
    response = urequests.get(url)

    try:
        if response.status_code != 200:
            raise RuntimeError("HTTP {}".format(response.status_code))

        monitors = ujson.loads(response.text)

        if not monitors:
            raise RuntimeError("Empty monitor list")

        print("Monitors:", monitors)
        return monitors
    finally:
        response.close()


# --- Main loop -------------------------------------------------------------

def main():
    print("UKW Client starting")
    show_message("UKW", C_WHITE)
    time.sleep(1)

    wlan = connect_wifi()
    if wlan is None:
        print("Retrying WiFi in 10 s ...")
        time.sleep(10)
        machine.reset()

    while True:
        set_led(LED_BLUE)
        try:
            monitors = poll_monitors()
            all_up = all(s == "up" for s in monitors.values())
            set_led(LED_GREEN if all_up else LED_RED)
            draw_monitors(monitors)
        except Exception as e:
            print("Error polling monitors:", e)
            set_led(LED_YELLOW)
            show_message("Error", C_YELLOW)

        time.sleep(POLL_INTERVAL)


main()
