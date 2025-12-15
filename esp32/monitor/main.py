import network
import time
import json
from umqtt.simple import MQTTClient
from machine import I2C, Pin
from lcd.machine_i2c_lcd import I2cLcd

# -----------------------------
# CONFIGURATION
# -----------------------------
WIFI_SSID = "Los Pollos Nuevos 2.4G"
WIFI_PASS = "3!4Fleschga@0"

MQTT_BROKER = "192.168.0.12"
MQTT_CLIENT_ID = "esp32-lcd"
MQTT_TOPIC = b"ubahn/#"

I2C_SCL = 22
I2C_SDA = 21
LCD_I2C_ADDR = 0x27
LCD_ROWS = 4
LCD_COLS = 20

STALE_TIMEOUT = 60  # seconds
# -----------------------------


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.2)

    print("\nConnected:", wlan.ifconfig()[0])


def init_lcd():
    i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
    lcd = I2cLcd(i2c, LCD_I2C_ADDR, LCD_ROWS, LCD_COLS)
    lcd.clear()
    lcd.putstr("Waiting MQTT...")
    return lcd


def normalize_text(t):
    if not isinstance(t, str):
        return ""

    replacements = {
        "Ü": "UE", "Ö": "OE", "Ä": "AE",
        "ü": "ue", "ö": "oe", "ä": "ae",
        "ß": "ss",
    }
    for bad, good in replacements.items():
        t = t.replace(bad, good)
    return t


def lcd_timeout():
    global lcd
    if lcd.backlight:
        lcd.backlight_off()
    lcd.clear()


def mqtt_callback(topic, msg):
    global lcd, last_update

    try:
        data = json.loads(msg.decode())
    except:
        lcd.clear()
        lcd.putstr("Invalid JSON")
        return

    departures = data.get("departures", [])
    idx = data.get("idx", 0)

    if idx == 0:
        lcd.clear()

    lines = []
    max_minutes = 0

    for d in departures:
        if len(lines) >= 2:
            break

        stop_name = normalize_text(d.get("towards"))
        minutes = d.get("minutes")

        if stop_name == "" or minutes is None:
            continue

        minutes_int = int(minutes)
        if minutes_int > max_minutes:
            max_minutes = minutes_int

        stop_name = stop_name[:17]

        if minutes == 0:
            minutes_disp = "*"
        else:
            minutes_disp = str(minutes)

        pad = 20 - len(stop_name) - len(minutes_disp)
        if pad < 0:
            pad = 0

        lines.append(stop_name + (" " * pad) + minutes_disp)

    while len(lines) < 2:
        lines.append(" " * 20)

    if max_minutes < 99:
        if not lcd.backlight:
            lcd.backlight_on()

        if idx == 1:
            lcd.move_to(0, 2)
        lcd.putstr(lines[0])

        if idx == 1:
            lcd.move_to(0, 3)
        else:
            lcd.move_to(0, 1)
        lcd.putstr(lines[1])

        last_update = time.time()

    else:
        lcd_timeout()


def main():
    global lcd, last_update
    import machine

    wifi_connect()
    lcd = init_lcd()

    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC)

    lcd.clear()
    lcd.putstr("MQTT connected!")

    last_update = time.time()

    while True:
        try:
            client.check_msg()
            time.sleep(0.1)

            # ---- stale data timeout ----
            if time.time() - last_update > STALE_TIMEOUT:
                lcd_timeout()

        except Exception as e:
            print("MQTT error:", e)
            time.sleep(2)
            machine.reset()


main()
