import ctypes

user32 = ctypes.windll.user32

# 声明回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def foreach_window(hwnd, lParam):
    """操作系统每发现一个窗口，就会把句柄 (hwnd) 传给这个函数"""
    if user32.IsWindowVisible(hwnd): # 只看当前屏幕上显示出来的窗口
        # 1. 抓取窗口标题 (Title)
        title_buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, title_buf, 512)
        
        # 2. 抓取窗口隐藏的类名 (Class Name)
        class_buf = ctypes.create_unicode_buffer(512)
        user32.GetClassNameW(hwnd, class_buf, 512)
        
        # 如果类名里包含 WeChat，或者你想通看所有窗口
        if "WeChat" in class_buf.value or title_buf.value:
            print(f"窗口句柄: {hwnd}")
            print(f"  └─ 屏幕上显示的Title : '{title_buf.value}'")
            print(f"  └─ 操作系统底层的ClassName: '{class_buf.value}'")
            print("-" * 50)
            
    return True # 返回 True 继续寻找下一个窗口

def main():
    print("[*] 正在扫描当前 Windows 系统中所有可见窗口的底层特征...")
    print("-" * 50)
    # 调用 Windows API 遍历所有窗口
    user32.EnumWindows(EnumWindowsProc(foreach_window), 0)

if __name__ == "__main__":
    main()
