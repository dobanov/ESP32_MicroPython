import network
import ntptime
import utime
import machine
import gc

gc.collect()

# Wi-Fi configuration
ssid = 'your_SSID'
password = 'your_PASSWORD'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connected to Wi-Fi')
print(station.ifconfig())

# Synchronize time using NTP
ntptime.host = 'pool.ntp.org'
ntptime.settime()

# Set timezone offset (UTC+3)
timezone_offset = 3 * 3600  # 3 hours in seconds

# Get current time and apply timezone offset
current_time = utime.time() + timezone_offset
local_time = utime.localtime(current_time)

# Format the time
year, month, day, hour, minute, second, weekday, yearday = local_time
milliseconds = utime.ticks_ms() % 1000

formatted_time = f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{milliseconds:03d}"

print('Time synchronized')
print('Current local time:', formatted_time)
