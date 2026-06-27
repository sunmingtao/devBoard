import threading
import time

def worker(num):
    print(f"worker {num} is working...")
    time.sleep(1)
    print(f"worker {num} is finished")

t1 = threading.Thread(target=worker, args=('1'))
t1.start()

# t1.join()

print("main finished")



from concurrent.futures import ThreadPoolExecutor
import time

def worker():
    print("worker start")
    time.sleep(3)
    print("worker finish")
    return 100

with ThreadPoolExecutor(max_workers=3) as executor:

    future = executor.submit(worker)

    print("main is doing something...")

    result = future.result()

    print(result)