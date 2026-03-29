from pathlib import Path
from time import monotonic

from utils import hash_password, load_secure_data, save_secure_data, verify_password


class AuthManager:
    def __init__(self, users_file: Path):
        self.users_file = users_file
        self.max_failed_attempts = 5
        self.lockout_seconds = 30
        self._failed_attempts: dict[str, int] = {}
        self._lockout_until: dict[str, float] = {}

    def _load_users(self) -> dict[str, str]:
        return load_secure_data(self.users_file, {})

    def _save_users(self, users: dict[str, str]) -> None:
        save_secure_data(self.users_file, users)

    def _check_lockout(self, username: str) -> int:
        lockout_end = self._lockout_until.get(username)
        if lockout_end is None:
            return 0
        remaining = int(lockout_end - monotonic())
        if remaining <= 0:
            self._lockout_until.pop(username, None)
            self._failed_attempts.pop(username, None)
            return 0
        return remaining

    def _record_failed_attempt(self, username: str) -> None:
        attempts = self._failed_attempts.get(username, 0) + 1
        self._failed_attempts[username] = attempts
        if attempts >= self.max_failed_attempts:
            self._lockout_until[username] = monotonic() + self.lockout_seconds

    def _clear_attempts(self, username: str) -> None:
        self._failed_attempts.pop(username, None)
        self._lockout_until.pop(username, None)

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

        remaining = self._check_lockout(cleaned_username)
        if remaining > 0:
            return False, f"Too many failed attempts. Try again in {remaining} seconds."

        if cleaned_username not in users:
            self._record_failed_attempt(cleaned_username)
            return False, "Invalid username or password."

        if not verify_password(password, users[cleaned_username]):
            self._record_failed_attempt(cleaned_username)
            return False, "Invalid username or password."

        self._clear_attempts(cleaned_username)
        return True, "Login successful."
