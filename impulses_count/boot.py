import network
import ntptime
import utime
import _thread  # Import the threading library
from config import WIFI_SSID, WIFI_PASSWORD
from web_server import start_web_server  # Import the web server function

# List of NTP servers to try
ntp_servers = ['pool.ntp.org', 'ntp1.ntp-servers.net', 'time.microsoft.com']

# Time zone setting
time_zone = 3  # UTC+3

# Function to connect to Wi-Fi
def connect_wifi(WIFI_SSID, WIFI_PASSWORD, retry_interval=5):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    while True:
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
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

# Function to monitor and maintain Wi-Fi connection
def maintain_wifi_connection(WIFI_SSID, WIFI_PASSWORD, check_interval=60):
    wifi = network.WLAN(network.STA_IF)
    while True:
        if not wifi.isconnected():
            print("Wi-Fi disconnected, attempting to reconnect...")
            connect_wifi(WIFI_SSID, WIFI_PASSWORD)
            get_ntp_time()  # Resynchronize time after reconnection
        utime.sleep(check_interval)

# Function to get NTP time and adjust RTC
def get_ntp_time():
    for server in ntp_servers:
        try:
            ntptime.host = server  # Set NTP server
            ntptime.settime()  # Synchronize time with the current NTP server
            print(f'Time synchronized with {server}')
            break
        except OSError as e:
            print(f"Failed to synchronize time with {server}: {e}")

# Attempt to connect to Wi-Fi
connect_wifi(WIFI_SSID, WIFI_PASSWORD)

# Get NTP time
get_ntp_time()

def web_server_task():
    print("Starting web server...")  # Debugging line
    start_web_server()

# Start the web server in a separate thread
_thread.start_new_thread(web_server_task, ())

# Start the Wi-Fi connection maintenance in a separate thread
_thread.start_new_thread(maintain_wifi_connection, (WIFI_SSID, WIFI_PASSWORD,))

# Output current time in specified format
current_time = utime.localtime()
print(f"{current_time[0] % 100:02d}/{current_time[1]:02d}/{current_time[2]:02d} {(current_time[3] + time_zone) % 24:02d}:{current_time[4]:02d}:{current_time[5]:02d}")
