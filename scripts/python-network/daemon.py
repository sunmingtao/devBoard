import threading
import time

def monitor():
    while True:
        print("monitoring...")
        time.sleep(1)

t = threading.Thread(target=monitor)
t.start()

time.sleep(3)

print("Bye")