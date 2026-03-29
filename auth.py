from pathlib import Path

from utils import hash_password, load_secure_data, save_secure_data, verify_password


class AuthManager:
    def __init__(self, users_file: Path):
        self.users_file = users_file

    def _load_users(self) -> dict[str, str]:
        return load_secure_data(self.users_file, {})

    def _save_users(self, users: dict[str, str]) -> None:
        save_secure_data(self.users_file, users)

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        cleaned_username = username.strip()
        if not cleaned_username:
            return False, "Username cannot be empty."
        if not password:
            return False, "Password cannot be empty."

        users = self._load_users()
        if cleaned_username in users:
            return False, "Username already exists."

        users[cleaned_username] = hash_password(password)
        self._save_users(users)
        return True, "Account created successfully. Please go to the log in page."

    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        users = self._load_users()
        cleaned_username = username.strip()

        if cleaned_username not in users:
            return False, "Invalid username or password."

        if not verify_password(password, users[cleaned_username]):
            return False, "Invalid username or password."

        return True, "Login successful."
