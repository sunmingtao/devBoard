with open("io_demo.txt", "w", encoding="utf-8") as f:
    f.write("Hello world\nHello world 2\n")

with open("io_demo.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())

with open("io_demo.txt", "a", encoding="utf-8") as f:
    f.write("Hello world 3")

with open("io_demo.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)