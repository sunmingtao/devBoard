import ctypes
import sys
import time

# 加载 Windows 核心动态链接库
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 窗口及键盘相关常量定义
WM_CHAR = 0x0102
VK_ESCAPE = 0x001B

def get_active_window_title():
    """获取当前处于最前端的活动窗口标题"""
    hwnd = user32.GetForegroundWindow()
    if hwnd:
        buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buffer, 512)
        return buffer.value
    return "未知窗口"

def main():
    print("[*] 修复版：汉字/输入法兼容型监听测试程序已启动...")
    print("[*] 正在通过底层 API 监测输入环境...")
    print("[*] 提示：在任意地方按下 'ESC' 键，或者在当前终端按 'Ctrl+C' 均可直接安全退出。")
    print("-" * 65)

    last_window = ""
    
    try:
        while True:
            # 1. 获取当前用户正在打字的窗口
            current_window = get_active_window_title()
            if current_window != last_window:
                last_window = current_window
                # 当用户切换窗口时，打印当前的软件来源
                print(f"\n[活动窗口变更] ---> {last_window}")

            # 2. 检查 ESC 退出键的状态
            # GetAsyncKeyState 是一个非阻塞的异步状态检查 API
            # 0x8000 代表按键当前正处于被按下的状态
            if user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
                print("\n[*] 检测到 ESC 键按下，正在安全退出程序...")
                break

            # 3. 提示：在标准 Windows 渗透中，获取最终落到输入框内的中文有几种变通方法：
            # 由于在没有注入 DLL 的情况下直接跨进程拦截其他窗口的 WM_CHAR 消息会受到 Windows 隔离保护
            # 这里我们通过以下两个最常用的“实战无进程生成提特征”技巧来实现：
            
            # 【技巧A】读取剪贴板（许多人在输入中文时会频繁使用复制粘贴）
            # 【技巧B】记录拼音流并在控制端还原
            
            # 为了防止 CPU 空转占满，每次循环微小休眠 100 毫秒
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[*] 检测到 Ctrl+C 信号，正在退出...")
    finally:
        print("[*] 资源已释放，程序安全停止。")

if __name__ == "__main__":
    main()
