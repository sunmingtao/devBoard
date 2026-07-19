import os
import sys
import time
import win32com.client

def log_to_file(message):
    """将监控到的进程日志写入本地文件"""
    with open("process_log.csv", "a", encoding="utf-8") as f:
        f.write(message + "\n")

def start_process_monitor():
    print("[*] WMI 进程安全审计模块已启动...")
    print("[*] 正在向 Windows 内核注册进程创建事件监听（__InstanceCreationEvent）...")
    print("[*] 提示：当后台的 BlackHatService 触发 VBS 脚本时，这里会立刻抓到现行！")
    print("-" * 75)

    # 写入 CSV 日志的文件头
    log_to_file("时间戳,进程名称,PID,父进程PID,启动用户,命令行参数")

    try:
        # 1. 连接到本地 Windows 的 WMI 核心命名空间
        obj_wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        obj_swbem_services = obj_wmi_service.ConnectServer(".", "root\\cimv2")

        # 2. 核心拦截指令：监听所有新创建的进程实例（Win32_Process）
        # Within 1 代表每隔 1 秒向内核轮询一次
        query = "SELECT * FROM __InstanceCreationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Process'"
        i_wbem_event_source = obj_swbem_services.ExecNotificationQuery(query)

        while True:
            # 3. 阻塞等待，直到 Windows 内核派发新进程创建的通知
            next_event = i_wbem_event_source.NextEvent()
            process_instance = next_event.TargetInstance

            # 4. 提取该进程的核心特征
            proc_name = process_instance.Name               # 进程名 (如 cscript.exe)
            proc_id = process_instance.ProcessId            # 进程 PID
            parent_id = process_instance.ParentProcessId      # 父进程 PID
            command_line = process_instance.CommandLine     # 完整的命令行参数
            
            # 如果命令行参数为空（某些系统核心隐藏进程），赋予默认值
            if not command_line:
                command_line = "N/A"

            # 5. 获取是谁拉起了这个进程（Owner / 用户权限等级）
            # 调用 Win32_Process 类的 GetOwner 方法
            owner_user = "Unknown"
            try:
                return_val = process_instance.GetOwner()
                if return_val[0] == 0:  # 0 代表获取成功
                    owner_user = f"{return_val[2]}\\{return_val[1]}" # 域名\用户名
            except Exception:
                pass

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 格式化输出
            # log_line = f"[{timestamp}] 发现新进程: {proc_name} (PID: {proc_id} | 父PID: {parent_id}) | 用户: {owner_user}"
            # print(log_line)
            # print(f"  └─ 完整参数: {command_line}")
            print(f"proc name is {proc_name.lower()}")

            # 同时保存到 CSV 以供后续分析
            csv_line = f"{timestamp},{proc_name},{proc_id},{parent_id},{owner_user},\"{command_line.replace('\"', '\"\"')}\""
            log_to_file(csv_line)

    except KeyboardInterrupt:
        print("\n[*] 进程监视器已被手动停止。")
    except Exception as e:
        print(f"[-] WMI 监听发生严重异常: {e}")

if __name__ == "__main__":
    start_process_monitor()
