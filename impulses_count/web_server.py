import socket
import utime
from file_rw import read_counter_from_file

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 Web Server</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 20px;
            padding: 20px;
        }}
        h1 {{
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .data-item {{
            margin-bottom: 10px;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .data-item:last-child {{
            border-bottom: none;
        }}
        .data-label {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 Data</h1>
        <div class="data-item">
            <span class="data-label">Current Time (UTC+3):</span> {current_time}
        </div>
        <div class="data-item">
            <span class="data-label">Cold:</span> {cold}
        </div>
        <div class="data-item">
            <span class="data-label">Hot:</span> {hot}
        </div>
    </div>
</body>
</html>
"""

# Function to adjust time for UTC+3
def adjust_time_for_utc_plus_3():
    local_time = list(utime.localtime())
    local_time[3] = (local_time[3] + 3) % 24  # Adjust for UTC+3
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(local_time[0], local_time[1], local_time[2], local_time[3], local_time[4], local_time[5])

# Function to handle client connections
def handle_client(conn):
    request = conn.recv(1024)
    print('Content = %s' % str(request))

    cold_value = read_counter_from_file('cold')
    hot_value = read_counter_from_file('hot')
    current_time = adjust_time_for_utc_plus_3()

    response = HTML_TEMPLATE.format(cold=cold_value, hot=hot_value, current_time=current_time)
    conn.sendall('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'.encode() + response.encode())
    conn.close()

# Function to start the web server
def start_web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set SO_REUSEADDR option
    s.bind(('', 80))
    s.listen(5)
    print('Web server started on port 80')

    while True:
        try:
            conn, addr = s.accept()
            print('Got connection from', addr)
            handle_client(conn)
        except Exception as e:
            print('Exception:', e)
            continue
