# services/auth_service.py
# Handles login, logout, and password changes (Module 1: Login System)

from database import load_data, save_data

FILENAME = "users.json"


class InvalidLoginError(Exception):
    """Raised when username doesn't exist."""
    pass


class WrongPasswordError(Exception):
    """Raised when the password doesn't match."""
    pass


def _ensure_default_admin():
    """
    If no users exist yet, creates a default Admin account so the app
    is never unusable on first run. Username: admin / Password: admin123
    """
    data = load_data(FILENAME)
    if "users" not in data:
        data = {"next_id": 1, "users": []}

    if len(data["users"]) == 0:
        data["users"].append({
            "user_id": 1,
            "username": "admin",
            "password": "admin123",   # NOTE: plain text for simplicity — not secure for real use
            "role": "Admin",
            "linked_employee_id": None
        })
        data["next_id"] = 2
        save_data(FILENAME, data)

    return data


def login(username, password):
    """
    Validates username + password. Returns the user dict on success.
    Raises InvalidLoginError if username doesn't exist,
    WrongPasswordError if password doesn't match.
    """
    data = _ensure_default_admin()
    users = data["users"]

    matched_user = None
    for u in users:
        if u["username"] == username:
            matched_user = u
            break

    if matched_user is None:
        raise InvalidLoginError(f"No account found with username '{username}'")

    if matched_user["password"] != password:
        raise WrongPasswordError("Incorrect password.")

    return matched_user


def change_password(username, old_password, new_password):
    """
    Changes a user's password after verifying the old one.
    """
    data = load_data(FILENAME)
    users = data.get("users", [])

    for u in users:
        if u["username"] == username:
            if u["password"] != old_password:
                raise WrongPasswordError("Current password is incorrect.")
            u["password"] = new_password
            save_data(FILENAME, data)
            return True

    raise InvalidLoginError(f"No account found with username '{username}'")


def add_user(username, password, role, linked_employee_id=None):
    """
    Creates a new login account. Used when registering an Operator
    or Delivery Boy who needs system access.
    """
    data = load_data(FILENAME)
    if "users" not in data:
        data = {"next_id": 1, "users": []}

    for u in data["users"]:
        if u["username"] == username:
            raise ValueError(f"Username '{username}' already exists.")

    new_id = data["next_id"]
    data["users"].append({
        "user_id": new_id,
        "username": username,
        "password": password,
        "role": role,
        "linked_employee_id": linked_employee_id
    })
    data["next_id"] += 1

    save_data(FILENAME, data)
    return new_id