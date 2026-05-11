import time
import network
from machine import Pin, I2C
import ssd1306
import secrets

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

sta = network.WLAN(network.STA_IF)
sta.active(True)

STAT_IDLE = getattr(network, "STAT_IDLE", None)
STAT_CONNECTING = getattr(network, "STAT_CONNECTING", None)
STAT_WRONG_PASSWORD = getattr(network, "STAT_WRONG_PASSWORD", None)
STAT_NO_AP_FOUND = getattr(network, "STAT_NO_AP_FOUND", None)
STAT_CONNECT_FAIL = getattr(network, "STAT_CONNECT_FAIL", None)
STAT_ASSOC_FAIL = getattr(network, "STAT_ASSOC_FAIL", None)
STAT_GOT_IP = getattr(network, "STAT_GOT_IP", None)

def s16(s):
    return (s or "")[:16]

def show(l1="", l2="", l3="", l4="", l5="", l6=""):
    oled.fill(0)
    oled.text(s16(l1), 0, 0, 1)
    oled.text(s16(l2), 0, 10, 1)
    oled.text(s16(l3), 0, 20, 1)
    oled.text(s16(l4), 0, 30, 1)
    oled.text(s16(l5), 0, 40, 1)
    oled.text(s16(l6), 0, 50, 1)
    oled.show()

def status_name(v):
    if v == STAT_IDLE:
        return "IDLE"
    if v == STAT_CONNECTING:
        return "CONNECTING"
    if v == STAT_WRONG_PASSWORD:
        return "WRONG PASS"
    if v == STAT_NO_AP_FOUND:
        return "NO AP FOUND"
    if v == STAT_CONNECT_FAIL:
        return "CONNECT FAIL"
    if v == STAT_ASSOC_FAIL:
        return "ASSOC FAIL"
    if v == STAT_GOT_IP:
        return "GOT IP"
    return str(v)

def connect_wifi(timeout_ms=15000):
    try:
        sta.disconnect()
    except:
        pass

    time.sleep(0.2)
    sta.connect(secrets.SSID, secrets.PASSWORD)

    t0 = time.ticks_ms()
    last = None

    while True:
        st = sta.status()
        if st != last:
            show(
                "WiFi connect...",
                "SSID:",
                s16(secrets.SSID),
                "STATUS:",
                status_name(st)
            )
            last = st

        if st == STAT_GOT_IP:
            return True, "connected"
        if st == STAT_WRONG_PASSWORD:
            return False, "wrong password"
        if st == STAT_NO_AP_FOUND:
            return False, "no ap found"
        if st == STAT_CONNECT_FAIL:
            return False, "connect fail"
        if st == STAT_ASSOC_FAIL:
            return False, "assoc fail"
        if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
            return False, "timeout"

        time.sleep(0.2)

def show_connected():
    rssi = sta.status("rssi")
    ip = sta.ifconfig()[0]

    oled.fill(0)
    oled.text("CONNECTED", 0, 0, 1)
    oled.text("SSID:", 0, 12, 1)
    oled.text(s16(secrets.SSID), 36, 12, 1)
    oled.text("RSSI:", 0, 24, 1)
    oled.text(str(rssi) + " dBm", 36, 24, 1)
    oled.text("IP:", 0, 36, 1)
    oled.text(s16(ip), 24, 36, 1)
    oled.show()

ok, msg = connect_wifi()

if ok:
    while True:
        show_connected()
        time.sleep(1)
else:
    while True:
        show(
            "WiFi ERROR",
            s16(msg),
            "SSID:",
            s16(secrets.SSID),
            "Check router/pass"
        )
        time.sleep(2)
