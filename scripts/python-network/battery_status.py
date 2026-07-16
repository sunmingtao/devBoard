import ctypes
from ctypes import wintypes

# 1. Define the C Structure matching the Windows API requirements
class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', wintypes.BYTE),
        ('BatteryFlag', wintypes.BYTE),
        ('BatteryLifePercent', wintypes.BYTE),
        ('SystemStatus', wintypes.BYTE),
        ('BatteryLifeTime', wintypes.DWORD),
        ('BatteryFullLifeTime', wintypes.DWORD),
    ]

# 2. Load kernel32.dll
kernel32 = ctypes.windll.kernel32

# 3. Explicitly declare argument and return types for safety
kernel32.GetSystemPowerStatus.argtypes = [ctypes.POINTER(SYSTEM_POWER_STATUS)]
kernel32.GetSystemPowerStatus.restype = wintypes.BOOL

# 4. Instantiate the structure and pass its reference via byref()
status = SYSTEM_POWER_STATUS()

if kernel32.GetSystemPowerStatus(ctypes.byref(status)):
    # 5. Extract values from the structure
    percent = status.BatteryLifePercent
    
    if percent == 255:
        print("Battery status unknown.")
    else:
        print(f"Battery Charge: {percent}%")
        
    if status.ACLineStatus == 1:
        print("Power Status: Plugged In")
    elif status.ACLineStatus == 0:
        print("Power Status: Running on Battery")
else:
    print("Failed to retrieve system power status.")
