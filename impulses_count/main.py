import gc
import machine
import utime
from reports import send_report  # Import the send_report function
from telegram import send_text_to_telegram  # Import the send_text_to_telegram function
from file_rw import read_counter_from_file, write_counter_to_file
from web_server import start_web_server  # Import the web server function
from config import BOT_TOKEN, CHAT_ID

# Initialize pins
pin14 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
pin12 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize variables
message_sent_14 = False
message_sent_12 = False

last_interrupt_time_14 = 0
last_interrupt_time_12 = 0

debounce_delay = 200   # Delay in milliseconds

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

def adjust_time_for_utc_plus_3():
    local_time = list(utime.localtime())
    local_time[3] = (local_time[3] + 3) % 24  # Adjust for UTC+3
    return local_time

def send_daily_report():
    local_time = adjust_time_for_utc_plus_3()
	# Check if it is 00:01 and send daily report
    if local_time[3] == 0 and local_time[4] == 1:
        send_report(BOT_TOKEN, CHAT_ID, 'daily')
        utime.sleep(60)

def send_monthly_report():
    local_time = adjust_time_for_utc_plus_3()
	# Check if it is 1st of the month and 00:01 and send monthly report
    if local_time[2] == 1 and local_time[3] == 0 and local_time[4] == 1:
        send_report(BOT_TOKEN, CHAT_ID, 'monthly')
        utime.sleep(60)

def other_logic_task():
    def periodic_report_timer_callback(timer):
        send_daily_report()
        send_monthly_report()

    periodic_report_timer = machine.Timer(-1)
    periodic_report_timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=periodic_report_timer_callback)

    try:
        while True:
            utime.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
        periodic_report_timer.deinit() 

# Start the web server
start_web_server()

try:
    other_logic_task()
except KeyboardInterrupt:
    print("Program terminated by user.")
