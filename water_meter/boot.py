import network
import ntptime
import utime
import machine
import gc

gc.collect()

# Wi-Fi configuration
ssid = 'your_SSID'
password = 'your_PASSWORD'

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

# Increase timeout for Wi-Fi connection
timeout = 20  # seconds
start_time = utime.time()
while not wifi.isconnected():
    if utime.time() - start_time > timeout:
        print("Wi-Fi connection timed out")
        break
    utime.sleep(1)

if wifi.isconnected():
    print('Connected to Wi-Fi')
    print('IP address:', wifi.ifconfig()[0])
    
    # List of NTP servers to try
    ntp_servers = ['pool.ntp.org', 'ntp1.ntp-servers.net', 'time.microsoft.com']
    
    # Attempt to synchronize time with multiple NTP servers
    for server in ntp_servers:
        try:
            ntptime.host = server
            ntptime.settime()
            print(f'Time synchronized with {server}')
            break  # Exit loop if synchronization successful
        except OSError as e:
            print(f"Failed to synchronize time with {server}: {e}")

    # Print current local time after synchronization
    current_time = utime.localtime()
    formatted_time = f"{current_time[0]}/{current_time[1]:02}/{current_time[2]:02} {current_time[3]:02}:{current_time[4]:02}:{current_time[5]:02}.{utime.ticks_ms() % 1000}"
    print('Current local time:', formatted_time)

else:
    print("Failed to connect to Wi-Fi")
