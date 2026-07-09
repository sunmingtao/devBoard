def args_test(*args):
    print("args:", args)
    print(args[3])  # output: 'mike'

args_test(1, 2, 3, 'mike')  # output: args: (1, 2, 3)

def add_numbers(num1, num2):
    total = num1 + num2
    print("Total:", total)

add_numbers(*[10, 5])  # output: Total: 15

def kwargs_test(**kwargs):
    print("kwargs:", kwargs)
    print(kwargs['name'])  # output: 'mike'   
    print(kwargs['age'])   # output: 30

kwargs_test(name='mike', age=30)  # output: kwargs: {'name': 'mike', 'age': 30}


def create_user(name, age, city):
    print(name, age, city)

user = {
    "name": "Mike",
    "age": 35,
    "city": "Canberra"
}

create_user(**user)  # output: Mike 35 Canberra