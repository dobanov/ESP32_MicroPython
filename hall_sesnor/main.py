import network
from time import sleep
from machine import Timer
import socket

# Параметры WiFi
SSID = 'your_SSID'
PASSWORD = 'your_PASSWORD'

# Подключение к WiFi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

while not station.isconnected():
    pass

print('Connection successful')
print('Network config:', station.ifconfig())

# Создание веб-страницы
def web_page(hall_value):
    html = """<html>
    <head>
        <meta http-equiv="refresh" content="2">
    </head>
    <body>
        <h1>Sensor Data</h1>
        <p>Current value: {}</p>
    </body>
    </html>""".format(hall_value)
    return html

# Функция обновления данных с датчика
def update_sensor(t):
    global hall_value
    hall_value = get_fake_sensor_value()
    print('Sensor value updated:', hall_value)

# Функция генерации фиктивного значения
def get_fake_sensor_value():
    import random
    return random.randint(-100, 100)

# Инициализация переменной для хранения значения датчика
hall_value = get_fake_sensor_value()

# Таймер для обновления данных каждые 2 секунды
timer = Timer(-1)
timer.init(period=2000, mode=Timer.PERIODIC, callback=update_sensor)

# Настройка веб-сервера
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)

print('Listening on', addr)

# Обработка запросов
while True:
    cl, addr = s.accept()
    print('Client connected from', addr)
    request = cl.recv(1024)
    request = str(request)
    response = web_page(hall_value)
    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
