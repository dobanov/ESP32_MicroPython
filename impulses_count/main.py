import gc
import machine
import uasyncio as asyncio
import utime
from reports import send_report  # Import the send_report function
from telegram import send_text_to_telegram  # Import the send_text_to_telegram function
from file_rw import read_counter_from_file, write_counter_to_file

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

# Function to handle other logic tasks
async def other_logic_task():
    while True:
        # Adjust time for UTC+3
        local_time = list(utime.localtime())
        local_time[3] = (local_time[3] + 3) % 24  # Adjust for UTC+3

        # Check if it is 00:01 and send daily report
        if local_time[3] == 0 and local_time[4] == 1:
            send_report(BOT_TOKEN, CHAT_ID, 'daily')
            await asyncio.sleep(300)  # Sleep for 5 minutes to avoid multiple reports within the same hour

        # Check if it is 1st of the month and 00:01 and send monthly report
        if local_time[2] == 1 and local_time[3] == 0 and local_time[4] == 1:
            send_report(BOT_TOKEN, CHAT_ID, 'monthly')
            await asyncio.sleep(300)  # Sleep for 5 minutes to avoid multiple reports within the same hour

        await asyncio.sleep(60)  # Regular check interval, adjust as needed
        gc.collect()  # Collect garbage to free up memory

async def main():
    await other_logic_task()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program terminated by user.")
