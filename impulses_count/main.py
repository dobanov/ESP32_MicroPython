import gc
import machine
import uasyncio as asyncio
import utime
import urequests
import ujson

# Telegram bot token and chat IDs
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID1,YOUR_CHAT_ID2"  # Separate multiple chat IDs with commas


# Initialize pins
pin14 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
pin12 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)

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
        try:
            response = urequests.post(url, headers=headers, data=payload)
            response.close()
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")

# Function to read counter from file
def read_counter_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return int(file.read())
    except (OSError, ValueError) as e:
        print(f"Failed to read from {filename}. Creating file...")
        write_counter_to_file(filename, 0)  # Create file if it doesn't exist
        return 0

# Function to write counter to file
def write_counter_to_file(filename, counter):
    try:
        with open(filename, 'w') as file:
            file.write(str(counter))
    except OSError as e:
        print(f"Failed to write to {filename}: {e}")

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
pin14.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=handle_pin14_interrupt)
pin12.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=handle_pin12_interrupt)

# Function to handle HTTP connections
async def handle_client(reader, writer):
    try:
        request = await reader.read(1024)
        request_str = request.decode('utf-8')
        print('Request:')
        print(request_str)

        # Generate HTML response with current time, hot, and cold values
        current_time = utime.localtime()
        formatted_time = f"{current_time[0] % 100:02d}/{current_time[1]:02d}/{current_time[2]:02d} {(current_time[3] + 3) % 24:02d}:{current_time[4]:02d}:{current_time[5]:02d}"

        # Read counters only once for efficiency
        hot_counter = read_counter_from_file('hot')
        cold_counter = read_counter_from_file('cold')

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
                    <span class="data-label">Hot:</span> {hot_counter}
                </div>
                <div class="data-item">
                    <span class="data-label">Cold:</span> {cold_counter}
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
        writer.write('\n'.join(response_headers).encode('utf-8'))
        writer.write(html.encode('utf-8'))
        await writer.drain()
    except Exception as e:
        print(f"Failed to handle HTTP connection: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

# Function to calculate daily consumption and send report
def send_daily_report():
    hot_last_day = read_counter_from_file('hot_last_day')
    hot_total = read_counter_from_file('hot')
    cold_last_day = read_counter_from_file('cold_last_day')
    cold_total = read_counter_from_file('cold')

    hot_this_day = hot_total - hot_last_day
    cold_this_day = cold_total - cold_last_day

    write_counter_to_file('hot_last_day', hot_total)
    write_counter_to_file('cold_last_day', cold_total)

    message = f"Daily report: {hot_this_day}0 liters of hot water and {cold_this_day}0 liters of cold water"
    send_text_to_telegram(BOT_TOKEN, CHAT_ID, message)
    print(message)

# Function to calculate monthly consumption and send report
def send_monthly_report():
    hot_last_month = read_counter_from_file('hot_last_month')
    hot_total = read_counter_from_file('hot')
    cold_last_month = read_counter_from_file('cold_last_month')
    cold_total = read_counter_from_file('cold')

    hot_this_month = hot_total - hot_last_month
    cold_this_month = cold_total - cold_last_month

    write_counter_to_file('hot_last_month', hot_total)
    write_counter_to_file('cold_last_month', cold_total)

    message = f"Monthly report: {hot_this_month}0 liters of hot water and {cold_this_month}0 liters of cold water"
    send_text_to_telegram(BOT_TOKEN, CHAT_ID, message)
    print(message)

# Function to handle other logic tasks
async def other_logic_task():
    while True:
        # Adjust time for UTC+3
        local_time = list(utime.localtime())
        local_time[3] = (local_time[3] + 3) % 24  # Adjust for UTC+3

        # Check if it is 00:01 and send daily report
        if local_time[3] == 0 and local_time[4] == 1:
            send_daily_report()
            await asyncio.sleep(300)  # Sleep for 5 minutes to avoid multiple reports within the same hour

        # Check if it is 1st of the month and 00:01 and send monthly report
        if local_time[2] == 1 and local_time[3] == 0 and local_time[4] == 1:
            send_monthly_report()
            await asyncio.sleep(300)  # Sleep for 5 minutes to avoid multiple reports within the same hour

        await asyncio.sleep(60)  # Regular check interval, adjust as needed
        gc.collect()  # Collect garbage to free up memory

async def main():
    await asyncio.gather(
        asyncio.start_server(handle_client, "0.0.0.0", 80),
        other_logic_task()
    )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program terminated by user.")
