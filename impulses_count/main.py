from machine import Pin
import utime
import urequests
import ujson

# Telegram bot token and chat IDs
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID1,YOUR_CHAT_ID2"  # Separate multiple chat IDs with commas

# Initialize pins
pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
pin12 = Pin(12, Pin.IN, Pin.PULL_UP)

# Initialize variables
message_sent_14 = False
message_sent_12 = False

last_interrupt_time_14 = 0
last_interrupt_time_12 = 0

debounce_delay = 200  # Delay in milliseconds

# Function to send a message to Telegram
def send_text_to_telegram(bot_token, chat_ids, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/json'}
    chat_ids_list = chat_ids.split(',')

    for chat_id in chat_ids_list:
        payload = ujson.dumps({"chat_id": chat_id, "text": message})
        response = urequests.post(url, headers=headers, data=payload)
        response.close()

# Function to read counter from file
def read_counter_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return int(file.read())
    except (OSError, ValueError):
        return 0

# Function to write counter to file
def write_counter_to_file(filename, counter):
    with open(filename, 'w') as file:
        file.write(str(counter))

# Function to handle pin interrupts
def handle_pin_interrupt(pin, pin_number, message_sent, last_interrupt_time, filename, description):
    current_time = utime.ticks_ms()

    if utime.ticks_diff(current_time, last_interrupt_time) > debounce_delay:
        pin_state = pin.value()
        if pin_state == 0:  # Short to GND
            if not message_sent:
                counter = read_counter_from_file(filename)
                counter += 1
                write_counter_to_file(filename, counter)
                message = f"Another 10 liters of {description} water leaked {counter}"
                print(message)
                send_text_to_telegram(BOT_TOKEN, CHAT_ID, message)
                message_sent = True
        else:  # Open from GND
            if message_sent:
                print(f"Open from GND detected on pin {pin_number}!")
                message_sent = False

        last_interrupt_time = current_time

    return message_sent, last_interrupt_time

# Pin interrupt handlers
def handle_pin14_interrupt(pin):
    global message_sent_14, last_interrupt_time_14
    message_sent_14, last_interrupt_time_14 = handle_pin_interrupt(pin, 14, message_sent_14, last_interrupt_time_14, 'cold', 'cold')

def handle_pin12_interrupt(pin):
    global message_sent_12, last_interrupt_time_12
    message_sent_12, last_interrupt_time_12 = handle_pin_interrupt(pin, 12, message_sent_12, last_interrupt_time_12, 'hot', 'hot')

# Configure interrupts for both pins
pin14.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin14_interrupt)
pin12.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin12_interrupt)

# Function to handle HTTP connections
def handle_http_connection(client_socket):
    request = client_socket.recv(1024)
    request_str = request.decode('utf-8')
    print('Request:')
    print(request_str)

    # Generate HTML response with current time, hot, and cold values
    current_time = utime.localtime()
    formatted_time = f"{current_time[0] % 100:02d}/{current_time[1]:02d}/{current_time[2]:02d} {(current_time[3] + time_zone) % 24:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ESP32 Data</title>
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
                <span class="data-label">Current Time:</span> {formatted_time}
            </div>
            <div class="data-item">
                <span class="data-label">Hot:</span> {read_counter_from_file('hot')}
            </div>
            <div class="data-item">
                <span class="data-label">Cold:</span> {read_counter_from_file('cold')}
            </div>
        </div>
    </body>
    </html>
    """

    # HTTP response headers
    response_headers = [
        'HTTP/1.1 200 OK',
        'Content-Type: text/html',
        'Connection: close',
        f'Content-Length: {len(html)}',
        '\n'
    ]

    # Send HTTP response
    client_socket.send('\n'.join(response_headers).encode('utf-8'))
    client_socket.send(html.encode('utf-8'))

    client_socket.close()

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', 80))
server_socket.listen(5)
print('Web server started on port 80')

# Main loop to handle incoming HTTP connections
try:
    while True:
        client_socket, addr = server_socket.accept()
        print('Client connected from:', addr)
        handle_http_connection(client_socket)
except KeyboardInterrupt:
    print("Program terminated by user.")
