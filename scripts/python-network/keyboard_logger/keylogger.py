import sys
from pynput import keyboard, mouse

def on_press(key):
    try:
        # 常规字母和数字键
        print(f"[键盘] 按下: {key.char}")
    except AttributeError:
        # 特殊功能键（如 Ctrl, Alt, Shift, 方向键等）
        print(f"[键盘] 特殊键按下: {key}")

def on_release(key):
    if key == keyboard.Key.esc:
        print("[*] 检测到 ESC 键，正在退出键盘监听...")
        return False  # 返回 False 可以停止当前监听器

def on_click(x, y, button, pressed):
    if pressed:
        print(f"[鼠标] 点击位置: ({x}, {y}) | 按键: {button}")
    else:
        print(f"[鼠标] 释放位置: ({x}, {y}) | 按键: {button}")

def main():
    print("[*] pynput 测试程序已启动...")
    print("[*] 正在监听全系统的键盘和鼠标事件...")
    print("[*] 提示：在任意窗口按下 'ESC' 键可安全退出本程序。\n" + "-"*40)

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
        keyboard_listener.join()

    mouse_listener.stop()
    print("[*] 程序已完全停止。")

if __name__ == "__main__":
    main()


# start cmd as admin
# cd C:\Users\Public\Downloads
# .venv\Scripts\activate
# pip install pynput
# python keylogger.py
