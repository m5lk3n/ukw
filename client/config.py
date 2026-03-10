from dotenv import load_dotenv

_env = load_dotenv()

# WiFi credentials
WIFI_SSID = _env.get("WIFI_SSID", "your-ssid")
WIFI_PASSWORD = _env.get("WIFI_PASSWORD", "your-password")

# UKW server
UKW_SERVER_URL = _env.get("UKW_SERVER_URL", "http://192.168.1.100:5000")

# Server polling interval in seconds
POLL_INTERVAL = int(_env.get("POLL_INTERVAL", "600"))

# Seconds each monitor page is shown before advancing to the next
PAGE_INTERVAL = int(_env.get("PAGE_INTERVAL", "5"))

# RGB LED (WS2812/NeoPixel) GPIO pin
LED_PIN = 38

# LCD pins (ST7789, Waveshare ESP32-S3-LCD-1.47)
LCD_DC_PIN  = 41
LCD_CS_PIN  = 42
LCD_CLK_PIN = 40
LCD_DIN_PIN = 45   # MOSI
LCD_RST_PIN = 39
LCD_BL_PIN  = 48

# LCD SPI bus id (1 or 2 on ESP32-S3)
LCD_SPI_ID = 1

# LCD SPI frequency (Hz)
LCD_SPI_FREQ = 40000000 # 80_000_000

# Display rotation (0 = portrait, 1 = landscape, 2 = portrait inverted, 3 = landscape inverted)
LCD_ROTATION = 3 # TODO/FIXME: portrait modes are mirrored/flipped, need to figure out why

# Font scale (1 = 8px, 2 = 16px, etc.)
FONT_SCALE = 2
