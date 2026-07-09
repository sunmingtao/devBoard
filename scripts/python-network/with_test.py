class Dog:
    def __init__(self):
        print("Dog init")

    def __enter__(self):
        print("Dog enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("Dog exit")
        

with Dog() as dog:
    print("Dog is running")
