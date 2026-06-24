from requests import get

def get_user(user_id):
    response = get(f"https://api.example.com/users/{user_id}")
    return response.json()
