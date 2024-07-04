from machine import I2C, Pin
import ssd1306
import time
import math

# Рисуем круг используя алгоритм Брезенхема
# Инициализация I2C
i2c = I2C(1, scl=Pin(22), sda=Pin(21))

# Создание объекта дисплея
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def draw_circle(oled, x0, y0, radius, color=1):
    f = 1 - radius
    ddF_x = 1
    ddF_y = -2 * radius
    x = 0
    y = radius

    oled.pixel(x0, y0 + radius, color)
    oled.pixel(x0, y0 - radius, color)
    oled.pixel(x0 + radius, y0, color)
    oled.pixel(x0 - radius, y0, color)

    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x

        oled.pixel(x0 + x, y0 + y, color)
        oled.pixel(x0 - x, y0 + y, color)
        oled.pixel(x0 + x, y0 - y, color)
        oled.pixel(x0 - x, y0 - y, color)
        oled.pixel(x0 + y, y0 + x, color)
        oled.pixel(x0 - y, y0 + x, color)
        oled.pixel(x0 + y, y0 - x, color)
        oled.pixel(x0 - y, y0 - x, color)

# Параметры круга
radius = 10
x = radius
y = 32

# Направление движения
dx = 2
dy = 1

while True:
    # Очищаем экран
    oled.fill(0)
    
    # Рисуем круг в новой позиции
    draw_circle(oled, x, y, radius)
    
    # Обновляем экран
    oled.show()
    
    # Обновляем координаты круга
    x += dx
    y += dy
    
    # Проверка границ экрана
    if x - radius < 0 or x + radius >= oled.width:
        dx = -dx
    if y - radius < 0 or y + radius >= oled.height:
        dy = -dy
    
    # Задержка для управления скоростью анимации
    time.sleep(0.05)
