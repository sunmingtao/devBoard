import ctypes
import os

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

SRCCOPY = 0xCC0020

# =====================================================================
# 关键修复点：加入 _pack_ = 1，强行让字节紧凑排列（1字节对齐）
# =====================================================================
class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1  # <--- 必须加上这一行！确保结构体精准为 14 字节
    _fields_ = [
        ("bfType", ctypes.c_ushort),
        ("bfSize", ctypes.c_ulong),
        ("bfReserved1", ctypes.c_ushort),
        ("bfReserved2", ctypes.c_ushort),
        ("bfOffBits", ctypes.c_ulong)
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1  # <--- 确保信息头完美紧凑（40 字节）
    _fields_ = [
        ("biSize", ctypes.c_ulong),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_ushort),
        ("biBitCount", ctypes.c_ushort),
        ("biCompression", ctypes.c_ulong),
        ("biSizeImage", ctypes.c_ulong),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_ulong),
        ("biClrImportant", ctypes.c_ulong)
    ]

def capture_screen_to_file(output_filename="screen.bmp"):
    width = user32.GetSystemMetrics(0)   
    height = user32.GetSystemMetrics(1)  
    
    hwnd_desktop = user32.GetDesktopWindow()
    hdc_screen = user32.GetWindowDC(hwnd_desktop)
    hdc_memory = gdi32.CreateCompatibleDC(hdc_screen)
    hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
    gdi32.SelectObject(hdc_memory, hbitmap)
    gdi32.BitBlt(hdc_memory, 0, 0, width, height, hdc_screen, 0, 0, SRCCOPY)
    
    bmih = BITMAPINFOHEADER()
    bmih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmih.biWidth = width
    bmih.biHeight = height
    bmih.biPlanes = 1
    bmih.biBitCount = 32  
    bmih.biCompression = 0 
    
    image_size = width * height * 4
    buffer = ctypes.create_string_buffer(image_size)
    gdi32.GetDIBits(hdc_screen, hbitmap, 0, height, buffer, ctypes.byref(bmih), 0)
    
    bmfh = BITMAPFILEHEADER()
    bmfh.bfType = 0x4D42 
    bmfh.bfSize = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER) + image_size
    bmfh.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
    
    # 打印调试信息，确保现在大小绝对正确了
    # 此时 sizeof(bmfh) 必须是 14，sizeof(bmih) 必须是 40
    print(f"[*] 结构体验证 -> 文件头: {ctypes.sizeof(bmfh)} 字节, 信息头: {ctypes.sizeof(bmih)} 字节")
    
    with open(output_filename, "wb") as f:
        f.write(bytes(bmfh))
        f.write(bytes(bmih))
        f.write(buffer)
        
    gdi32.DeleteObject(hbitmap)
    gdi32.DeleteDC(hdc_memory)
    user32.ReleaseDC(hwnd_desktop, hdc_screen)
    
    print(f"[+] 修复完成！请重新双击打开: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    capture_screen_to_file()
