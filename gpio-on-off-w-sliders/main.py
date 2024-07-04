from machine import Pin, PWM, reset
import socket
import ujson

# Initialize the LEDs with PWM for brightness control
led_14 = PWM(Pin(14), freq=5000)
led_12 = PWM(Pin(12), freq=5000)
led_13 = PWM(Pin(13), freq=5000)

# Function to save the LED states to a file
def save_led_states(states):
    try:
        with open('led_states.json', 'w') as f:
            ujson.dump(states, f)
    except Exception as e:
        print('Failed to save LED states:', e)

# Function to load the LED states from a file
def load_led_states():
    try:
        with open('led_states.json', 'r') as f:
            states = ujson.load(f)
            # Ensure all keys exist and have valid values
            for key in ['led_14_brightness', 'led_14_state', 'led_12_brightness', 'led_12_state', 'led_13_brightness', 'led_13_state']:
                if key not in states:
                    states[key] = 0  # Set default value if key is missing
            return states
    except Exception as e:
        print('Failed to load LED states:', e)
        return {
            'led_14_brightness': 0,
            'led_14_state': 0,
            'led_12_brightness': 0,
            'led_12_state': 0,
            'led_13_brightness': 0,
            'led_13_state': 0
        }

# Load initial LED states
led_states = load_led_states()
led_14.duty(led_states['led_14_brightness'] if led_states['led_14_state'] == 1 else 0)
led_12.duty(led_states['led_12_brightness'] if led_states['led_12_state'] == 1 else 0)
led_13.duty(led_states['led_13_brightness'] if led_states['led_13_state'] == 1 else 0)

def web_page():
    # Create the HTML page
    html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}.slider{width: 100%;}</style></head><body> <h1>ESP Web Server</h1>
    <p>GPIO 14 state: <strong>""" + ("ON" if led_states['led_14_state'] == 1 else "OFF") + """</strong></p>
    <p>GPIO 12 state: <strong>""" + ("ON" if led_states['led_12_state'] == 1 else "OFF") + """</strong></p>
    <p>GPIO 13 state: <strong>""" + ("ON" if led_states['led_13_state'] == 1 else "OFF") + """</strong></p>
    <p><a href="/?led14=on"><button class="button">ON</button></a>
    <a href="/?led14=off"><button class="button button2">OFF</button></a></p>
    <p><a href="/?led12=on"><button class="button">ON</button></a>
    <a href="/?led12=off"><button class="button button2">OFF</button></a></p>
    <p><a href="/?led13=on"><button class="button">ON</button></a>
    <a href="/?led13=off"><button class="button button2">OFF</button></a></p>
    <p>LED 14 Brightness: <input type="range" min="0" max="1023" value=""" + str(led_states['led_14_brightness']) + """ class="slider" id="led14_brightness" onchange="updateBrightness(14, this.value)">
    <p>LED 12 Brightness: <input type="range" min="0" max="1023" value=""" + str(led_states['led_12_brightness']) + """ class="slider" id="led12_brightness" onchange="updateBrightness(12, this.value)">
    <p>LED 13 Brightness: <input type="range" min="0" max="1023" value=""" + str(led_states['led_13_brightness']) + """ class="slider" id="led13_brightness" onchange="updateBrightness(13, this.value)">
    <script>
    function updateBrightness(led, value) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "/?led" + led + "_brightness=" + value, true);
        xhr.send();
    }
    </script>
    </body></html>"""
    return html

def handle_client(conn):
    try:
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
        led14_brightness = request.find('/?led14_brightness=')
        led12_brightness = request.find('/?led12_brightness=')
        led13_brightness = request.find('/?led13_brightness=')

        if led14_on == 6:
            print('LED 14 ON')
            led_states['led_14_state'] = 1
            led_14.duty(led_states['led_14_brightness'])
        elif led14_off == 6:
            print('LED 14 OFF')
            led_states['led_14_state'] = 0
            led_14.duty(0)
        elif led14_brightness != -1:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 14 Brightness:', brightness)
            led_states['led_14_brightness'] = brightness
            if led_states['led_14_state'] == 1:
                led_14.duty(brightness)

        if led12_on == 6:
            print('LED 12 ON')
            led_states['led_12_state'] = 1
            led_12.duty(led_states['led_12_brightness'])
        elif led12_off == 6:
            print('LED 12 OFF')
            led_states['led_12_state'] = 0
            led_12.duty(0)
        elif led12_brightness != -1:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 12 Brightness:', brightness)
            led_states['led_12_brightness'] = brightness
            if led_states['led_12_state'] == 1:
                led_12.duty(brightness)

        if led13_on == 6:
            print('LED 13 ON')
            led_states['led_13_state'] = 1
            led_13.duty(led_states['led_13_brightness'])
        elif led13_off == 6:
            print('LED 13 OFF')
            led_states['led_13_state'] = 0
            led_13.duty(0)
        elif led13_brightness != -1:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 13 Brightness:', brightness)
            led_states['led_13_brightness'] = brightness
            if led_states['led_13_state'] == 1:
                led_13.duty(brightness)

        save_led_states(led_states)

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
