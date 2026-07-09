x = 1

def change():
    global x
    x = 2

print(x)   # 1
change()
print(x)   # 2