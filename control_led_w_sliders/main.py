from machine import Pin, PWM, reset, Timer
import socket

# Initialize PWM for LEDs
led_14 = PWM(Pin(14), freq=1000)
led_12 = PWM(Pin(12), freq=1000)
led_13 = PWM(Pin(13), freq=1000)

# Watchdog Timer setup (2 minutes timeout)
wdt = Timer(1)
wdt.init(period=120000, mode=Timer.PERIODIC, callback=lambda t: reset())

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
        if '/?led12=' in request:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 12 Brightness:', brightness)
            led_12.duty(brightness)
        if '/?led13=' in request:
            brightness = int(request.split('=')[1].split(' ')[0])
            print('LED 13 Brightness:', brightness)
            led_13.duty(brightness)

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
