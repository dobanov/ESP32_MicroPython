from machine import Pin
import utime

pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
pin12 = Pin(12, Pin.IN, Pin.PULL_UP)

message_sent_14 = False
message_sent_12 = False

last_interrupt_time_14 = 0
last_interrupt_time_12 = 0

debounce_delay = 200  # Delay in milliseconds

def handle_pin_interrupt(pin, pin_number, message_sent, last_interrupt_time):
    current_time = utime.ticks_ms()
    
    if utime.ticks_diff(current_time, last_interrupt_time) > debounce_delay:
        pin_state = pin.value()
        if pin_state == 0:  # Short to GND
            if not message_sent:
                print(f"Short to GND detected on pin {pin_number}!")
                message_sent = True
        else:  # Open from GND
            if message_sent:
                print(f"Open from GND detected on pin {pin_number}!")
                message_sent = False
                
        last_interrupt_time = current_time

    return message_sent, last_interrupt_time

def handle_pin14_interrupt(pin):
    global message_sent_14, last_interrupt_time_14
    message_sent_14, last_interrupt_time_14 = handle_pin_interrupt(pin, 14, message_sent_14, last_interrupt_time_14)

def handle_pin12_interrupt(pin):
    global message_sent_12, last_interrupt_time_12
    message_sent_12, last_interrupt_time_12 = handle_pin_interrupt(pin, 12, message_sent_12, last_interrupt_time_12)

# Configure interrupts for both pins
pin14.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin14_interrupt)
pin12.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=handle_pin12_interrupt)

try:
    while True:
        utime.sleep_ms(100)
except KeyboardInterrupt:
    print("Program terminated by user.")
