import sys
from microbit import *

buttons = ['button_a', 'button_b']
sys.argv.extend(buttons)

button = sys.argv[1] if (sys.argv[1] in buttons) else buttons[0]

while True:
    state.press_and_release(button)
