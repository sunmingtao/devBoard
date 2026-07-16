import sys
import time
import random
from pynput import keyboard, mouse

keystrokes = 0
mouse_clicks = 0
double_clicks = 0
previous_timestamp = None

double_click_threshold = 0.25

def on_press(key):
    global keystrokes, previous_timestamp, double_clicks
    keystrokes += 1

    current_time = time.time()
    if previous_timestamp is not None:
        elapsed = current_time - previous_timestamp
        if elapsed <= double_click_threshold:
            double_clicks += 1
    previous_timestamp = current_time

def on_click(x, y, button, pressed):
    global mouse_clicks
    if pressed:
        mouse_clicks += 1

def detect_sandbox():
    global mouse_clicks, keystrokes, double_clicks

    max_keystrokes = random.randint(10, 20)
    max_mouse_clicks = random.randint(5,15)
    max_double_clicks = 5

    k_listener = keyboard.Listener(on_press=on_press)
    m_listener = mouse.Listener(on_click=on_click)
    k_listener.start()
    m_listener.start()

    try:
        while True:
            if keyboard >= max_keystrokes and mouse_clicks >= max_mouse_clicks and double_clicks >= max_double_clicks:
                print('Pass')
                break

            time.sleep(0.1)
    finally:
        k_listener.stop()
        m_listener.stop()

if __name__ == "__main__":
    detect_sandbox()
    print('Start Git Trojan')
