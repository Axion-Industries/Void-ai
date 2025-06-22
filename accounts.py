import json
import os
from werkzeug.security import generate_password_hash, check_password_hash


USERS_FILE = "users.json"


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def create_account(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = {"password_hash": generate_password_hash(password)}
    save_users(users)
    return True, "Account created!"


def login(username, password):
    users = load_users()
    user_data = users.get(username)
    if user_data and check_password_hash(user_data["password_hash"], password):
        return True, "Login successful!"
    return False, "Invalid credentials."


def get_user_data_file(username):
    return f"input_{username}.txt"
