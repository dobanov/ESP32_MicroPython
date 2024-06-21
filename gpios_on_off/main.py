from machine import Pin
import socket

# Initialize the hall sensor and LEDs
led_14 = Pin(14, Pin.OUT)
led_12 = Pin(12, Pin.OUT)
led_13 = Pin(13, Pin.OUT)

def web_page():
    # Get the states of the GPIOs
    gpio_14_state = "ON" if led_14.value() == 1 else "OFF"
    gpio_12_state = "ON" if led_12.value() == 1 else "OFF"
    gpio_13_state = "ON" if led_13.value() == 1 else "OFF"

    # Create the HTML page
    html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1>
    <p>GPIO 14 state: <strong>""" + gpio_14_state + """</strong></p>
    <p>GPIO 12 state: <strong>""" + gpio_12_state + """</strong></p>
    <p>GPIO 13 state: <strong>""" + gpio_13_state + """</strong></p>
    <p><a href="/?led14=on"><button class="button">ON</button></a>
    <a href="/?led14=off"><button class="button button2">OFF</button></a></p>
    <p><a href="/?led12=on"><button class="button">ON</button></a>
    <a href="/?led12=off"><button class="button button2">OFF</button></a></p>
    <p><a href="/?led13=on"><button class="button">ON</button></a>
    <a href="/?led13=off"><button class="button button2">OFF</button></a></p>
    </body></html>"""
    return html

# Set up the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)

    # Parse the request to control LEDs
    led14_on = request.find('/?led14=on')
    led14_off = request.find('/?led14=off')
    led12_on = request.find('/?led12=on')
    led12_off = request.find('/?led12=off')
    led13_on = request.find('/?led13=on')
    led13_off = request.find('/?led13=off')

    if led14_on == 6:
        print('LED 14 ON')
        led_14.value(1)
    if led14_off == 6:
        print('LED 14 OFF')
        led_14.value(0)
    if led12_on == 6:
        print('LED 12 ON')
        led_12.value(1)
    if led12_off == 6:
        print('LED 12 OFF')
        led_12.value(0)
    if led13_on == 6:
        print('LED 13 ON')
        led_13.value(1)
    if led13_off == 6:
        print('LED 13 OFF')
        led_13.value(0)

    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
