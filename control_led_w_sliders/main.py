from machine import Pin, PWM, reset, Timer
import socket
import ujson

# Initialize PWM for LEDs
led_14 = PWM(Pin(14), freq=1000)
led_12 = PWM(Pin(12), freq=1000)
led_13 = PWM(Pin(13), freq=1000)

# Function to save the brightness values to a file
def save_brightness(brightness_values):
    try:
        with open('brightness.json', 'w') as f:
            ujson.dump(brightness_values, f)
    except Exception as e:
        print('Failed to save brightness values:', e)

# Function to load the brightness values from a file
def load_brightness():
    try:
        with open('brightness.json', 'r') as f:
            return ujson.load(f)
    except:
        return {'led_14': 0, 'led_12': 0, 'led_13': 0}

# Load initial brightness values
brightness_values = load_brightness()
led_14.duty(brightness_values['led_14'])
led_12.duty(brightness_values['led_12'])
led_13.duty(brightness_values['led_13'])

# Watchdog Timer setup (2 minutes timeout)
wdt = Timer(1)
wdt.init(period=36000000, mode=Timer.PERIODIC, callback=lambda t: reset())

def web_page():
    # Create the HTML page with sliders
    html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.slider{width: 300px;}</style></head><body> <h1>ESP Web Server</h1>
    <p>LED 14 Brightness: <strong>""" + str(led_14.duty()) + """</strong></p>
    <p><input type="range" min="0" max="1023" value="""" + str(led_14.duty()) + """" class="slider" id="led14Slider" onchange="updateLED('14', this.value)"></p>
    <p>LED 12 Brightness: <strong>""" + str(led_12.duty()) + """</strong></p>
    <p><input type="range" min="0" max="1023" value="""" + str(led_12.duty()) + """" class="slider" id="led12Slider" onchange="updateLED('12', this.value)"></p>
    <p>LED 13 Brightness: <strong>""" + str(led_13.duty()) + """</strong></p>
    <p><input type="range" min="0" max="1023" value="""" + str(led_13.duty()) + """" class="slider" id="led13Slider" onchange="updateLED('13', this.value)"></p>
    <script>
    function updateLED(led, brightness) {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/?led" + led + "=" + brightness, true);
        xhttp.send();
    }
    </script>
    </body></html>"""
    return html

def handle_client(conn):
    try:
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)

        # Parse the request to control LED brightness
        if '/?led14=' in request:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 14 Brightness:', brightness)
            led_14.duty(brightness)
            brightness_values['led_14'] = brightness
        if '/?led12=' in request:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 12 Brightness:', brightness)
            led_12.duty(brightness)
            brightness_values['led_12'] = brightness
        if '/?led13=' in request:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 13 Brightness:', brightness)
            led_13.duty(brightness)
            brightness_values['led_13'] = brightness

        save_brightness(brightness_values)

        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
    except Exception as e:
        print('Error:', e)
        reset()
    finally:
        conn.close()

# Set up the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set SO_REUSEADDR option
s.bind(('', 80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        handle_client(conn)
    except Exception as e:
        print('Error:', e)
        reset()
