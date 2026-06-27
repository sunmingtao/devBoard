from concurrent.futures import ThreadPoolExecutor
import time

def square(n):
    time.sleep(1)
    return n * n

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(square, range(5)[::-1])
    for result in results:
        print(result)