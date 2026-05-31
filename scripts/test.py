import os
from pathlib import Path
import subprocess
from time import time
import time

CHUNK_DIR = Path("/home/jacky/workspace/devBoard/scripts/whisper-env/chunks")

print("Testing chunk files:")

glob_result = sorted(CHUNK_DIR.glob("chunk_*.wav"))
abc='abc'
print(f"{abc=}")

file='iiio-kkkC.mp4'

if '~' in file:
    print("File contains tilde.")
else:
    print("File does not contain tilde.")

start_time = time.perf_counter() # 高精度计时器
time.sleep(2)  # 模拟某个操作耗时2秒
end_time = time.perf_counter()
    
elapsed_time = end_time - start_time
print(f"Main 函数耗时: {elapsed_time:.4f} 秒")

# for chunk_index, chunk_file in enumerate(sorted(CHUNK_DIR.glob("chunk_*.wav"))):
#     print(f"Processing chunk {chunk_index}: {chunk_file}")
#     print(str(chunk_file))
#     print(f"Chunk file path: {chunk_file}")