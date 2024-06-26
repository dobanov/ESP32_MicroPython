
import network
import ntptime
import utime
import sys
from machine import RTC

# Wi-Fi configuration
ssid = 'your_SSID'
password = 'your_PASSWORD'

# List of NTP servers to try
ntp_servers = ['pool.ntp.org', 'ntp1.ntp-servers.net', 'time.microsoft.com']

# Time zone setting
time_zone = 3  # UTC+3

# Function to connect to Wi-Fi
def connect_wifi(ssid, password, retry_interval=5):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    while True:
        wifi.connect(ssid, password)
        print("Attempting to connect to Wi-Fi...")

        start_time = utime.time()
        while not wifi.isconnected():
            if utime.time() - start_time > retry_interval:
                print("Wi-Fi connection attempt failed, retrying...")
                break
            utime.sleep(1)

        if wifi.isconnected():
            print('Connected to Wi-Fi')
            print('IP address:', wifi.ifconfig())
            return True


# Function to get NTP time and adjust RTC
def get_ntp_time():
    rtc = RTC()
    for server in ntp_servers:
        try:
            ntptime.host = server  # Set NTP server
            ntptime.settime()  # Synchronize time with the current NTP server
            print(f'Time synchronized with {server}')
            rtc.datetime((rtc.datetime()[0], rtc.datetime()[1], rtc.datetime()[2], (rtc.datetime()[3] + time_zone) % 24, rtc.datetime()[4], rtc.datetime()[5], rtc.datetime()[6], rtc.datetime()[7] + time_zone * 3600))
            break
        except OSError as e:
            print(f"Failed to synchronize time with {server}: {e}")

# Attempt to connect to Wi-Fi
connect_wifi(ssid, password)

# Get NTP time
get_ntp_time()

# Output current time in specified format
current_time = utime.localtime()
print(f"{current_time[0] % 100:02d}/{current_time[1]:02d}/{current_time[2]:02d} {(current_time[3] + time_zone) % 24:02d}:{current_time[4]:02d}:{current_time[5]:02d}.{utime.time() % 1 * 1000:03.0f}")
