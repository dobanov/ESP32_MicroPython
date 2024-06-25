from machine import Pin
import utime
import urequests
import ujson

# Telegram bot token and chat IDs
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID1,YOUR_CHAT_ID2"  # Separate multiple chat IDs with commas

pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
pin12 = Pin(12, Pin.IN, Pin.PULL_UP)

message_sent_14 = False
message_sent_12 = False

last_interrupt_time_14 = 0
last_interrupt_time_12 = 0

debounce_delay = 200  # Delay in milliseconds

def send_text_to_telegram(bot_token, chat_ids, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/json'}
    chat_ids_list = chat_ids.split(',')

    for chat_id in chat_ids_list:
        payload = ujson.dumps({"chat_id": chat_id, "text": message})
        response = urequests.post(url, headers=headers, data=payload)
        response.close()

def read_counter_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return int(file.read())
    except (OSError, ValueError):
        return 0

def write_counter_to_file(filename, counter):
    with open(filename, 'w') as file:
        file.write(str(counter))

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

def handle_pin14_interrupt(pin):
    global message_sent_14, last_interrupt_time_14
    message_sent_14, last_interrupt_time_14 = handle_pin_interrupt(pin, 14, message_sent_14, last_interrupt_time_14, 'cold', 'Cold count')

def handle_pin12_interrupt(pin):
    global message_sent_12, last_interrupt_time_12
    message_sent_12, last_interrupt_time_12 = handle_pin_interrupt(pin, 12, message_sent_12, last_interrupt_time_12, 'hot', 'Hot count')

# Configure interrupts for both pins
pin14.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin14_interrupt)
pin12.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin12_interrupt)

try:
    while True:
        utime.sleep_ms(100)
except KeyboardInterrupt:
    print("Program terminated by user.")
