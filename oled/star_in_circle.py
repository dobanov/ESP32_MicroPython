from machine import Pin, I2C
import ssd1306
import time
import math

# ESP32 Pin assignment
i2c = I2C(0, scl=Pin(18), sda=Pin(19))

# Создание объекта дисплея
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def draw_line(oled, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        oled.pixel(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def draw_star(oled, x0, y0, size, color=1):
    points = []
    for i in range(5):
        angle = math.radians(72 * i - 130)  # -90 для перевернутой звезды
        x = x0 + size * math.cos(angle)
        y = y0 + size * math.sin(angle)
        points.append((x, y))

    for i in range(5):
        draw_line(oled, int(points[i][0]), int(points[i][1]),
                  int(points[(i + 2) % 5][0]), int(points[(i + 2) % 5][1]), color)

def draw_circle(oled, x0, y0, radius, color=1):
    x = radius
    y = 0
    err = 0

    while x >= y:
        oled.pixel(x0 + x, y0 + y, color)
        oled.pixel(x0 + y, y0 + x, color)
        oled.pixel(x0 - y, y0 + x, color)
        oled.pixel(x0 - x, y0 + y, color)
        oled.pixel(x0 - x, y0 - y, color)
        oled.pixel(x0 - y, y0 - x, color)
        oled.pixel(x0 + y, y0 - x, color)
        oled.pixel(x0 + x, y0 - y, color)

        if err <= 0:
            y += 1
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1

# Параметры звезды
star_size = 10
star_x = star_size
star_y = 32

# Параметры круга
circle_radius = star_size + 2

# Направление движения звезды
dx = 2
dy = 1

while True:
    # Очищаем экран
    oled.fill(0)

    # Рисуем круг вокруг звезды
    draw_circle(oled, star_x, star_y, circle_radius)

    # Рисуем звезду в новой позиции
    draw_star(oled, star_x, star_y, star_size)

    # Обновляем экран
    oled.show()

    # Обновляем координаты звезды
    star_x += dx
    star_y += dy

    # Проверка границ экрана
    if star_x - star_size < 0 or star_x + star_size >= oled.width:
        dx = -dx
    if star_y - star_size < 0 or star_y + star_size >= oled.height:
        dy = -dy

    # Задержка для управления скоростью анимации
    time.sleep(0.05)

