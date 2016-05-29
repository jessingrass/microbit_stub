from microbit_stub import *

while True:
    if button_a.is_pressed():
        for i in range(5):
            if display.get_pixel(i, 0):
                display.set_pixel(i, 0, 0)
                sleep(10)
            else:
                display.set_pixel(i, 0, 9)
                sleep(200)
                break
    elif button_b.is_pressed():
        n = 0
        for i in range(5):
            if display.get_pixel(i, 0):
                n = n + 2 ** i

        display.clear()
        display.show(str(n))
        sleep(1000)
        display.clear()
        break
    else:
        sleep(50)
