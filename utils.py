import base64
import hashlib
import hmac
import json
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any


LEGACY_APP_SECRET = b"quiz-app-local-secret"
SECRET_ENV_VAR = "QUIZ_APP_SECRET"
SECRET_FILE = ".quiz_app_secret"
PBKDF2_ITERATIONS = 200_000


def project_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


def _load_app_secret() -> bytes:
    env_secret = os.getenv(SECRET_ENV_VAR, "").strip()
    if env_secret:
        return env_secret.encode("utf-8")

    secret_path = project_path(SECRET_FILE)
    if secret_path.exists():
        try:
            content = secret_path.read_text(encoding="utf-8").strip()
            if content:
                return content.encode("utf-8")
        except OSError:
            pass

    generated_secret = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
    try:
        secret_path.write_text(generated_secret, encoding="utf-8")
        try:
            os.chmod(secret_path, 0o600)
        except OSError:
            pass
    except OSError:
        return LEGACY_APP_SECRET
    return generated_secret.encode("utf-8")


def _xor_bytes(raw: bytes, key: bytes) -> bytes:
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(raw))


def _derived_key(secret: bytes) -> bytes:
    return hashlib.sha256(secret).digest()


def encode_data(payload: Any) -> str:
    serialized = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encrypted = _xor_bytes(serialized, _derived_key(_load_app_secret()))
    return base64.urlsafe_b64encode(encrypted).decode("utf-8")


def _decode_payload(encoded_text: str) -> tuple[bool, Any]:
    try:
        encrypted = base64.urlsafe_b64decode(encoded_text.encode("utf-8"))
    except Exception:
        return False, None

    candidate_secrets = [_load_app_secret(), LEGACY_APP_SECRET]
    for secret in candidate_secrets:
        try:
            serialized = _xor_bytes(encrypted, _derived_key(secret))
            return True, json.loads(serialized.decode("utf-8"))
        except Exception:
            continue
    return False, None


def decode_data(encoded_text: str, default: Any) -> Any:
    if not encoded_text.strip():
        return default
    ok, payload = _decode_payload(encoded_text)
    if not ok:
        return default
    return payload


def save_secure_data(file_path: Path, payload: Any) -> None:
    try:
        file_path.write_text(encode_data(payload), encoding="utf-8")
    except OSError as exc:
        print(f"Could not save data to {file_path.name}: {exc}")


def load_secure_data(file_path: Path, default: Any) -> Any:
    if not file_path.exists():
        save_secure_data(file_path, default)
        return default
    try:
        encoded_text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Could not read data from {file_path.name}: {exc}")
        return default

    if not encoded_text.strip():
        return default

    ok, payload = _decode_payload(encoded_text)
    if ok:
        return payload

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = file_path.with_suffix(f"{file_path.suffix}.corrupt.{timestamp}")
    try:
        file_path.replace(backup_path)
        print(
            f"Warning: {file_path.name} is corrupted. Backup created as {backup_path.name}. "
            "Starting with default data."
        )
    except OSError as exc:
        print(
            f"Warning: {file_path.name} appears corrupted and could not be backed up: {exc}. "
            "Starting with default data."
        )

    return default


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return hmac.compare_digest(digest, expected)


def question_id(question: dict[str, Any]) -> str:
    key_fields = [
        question.get("question", ""),
        question.get("answer", ""),
        question.get("category", ""),
        question.get("difficulty", ""),
    ]
    joined = "||".join(str(field) for field in key_fields)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def build_hint(question: dict[str, Any]) -> str:
    answer = str(question.get("answer", "")).strip()
    if not answer:
        return "No hint available."
    question_type = question.get("type", "")
    if question_type == "multiple_choice":
        return f"Hint: starts with '{answer[0]}'."
    if question_type == "true_false":
        return "Hint: answer is either true or false."
    visible = max(1, len(answer) // 3)
    masked = answer[:visible] + "_" * (len(answer) - visible)
    return f"Hint: {masked}"


def calculate_category_averages(score_history: list[dict[str, Any]]) -> dict[str, float]:
    by_category: dict[str, list[float]] = {}
    for record in score_history:
        category = record.get("category")
        percentage = record.get("percentage")
        if category is None or percentage is None:
            continue
        by_category.setdefault(category, []).append(float(percentage))
    return {
        category: (sum(percentages) / len(percentages))
        for category, percentages in by_category.items()
        if percentages
    }


def weighted_sample_without_replacement(
    items: list[dict[str, Any]],
    weights: list[float],
    sample_size: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    pool = list(items)
    weight_pool = list(weights)

    for _ in range(min(sample_size, len(pool))):
        total = sum(weight_pool)
        if total <= 0:
            index = random.randrange(len(pool))
        else:
            target = random.uniform(0, total)
            running = 0.0
            index = 0
            for candidate_index, weight in enumerate(weight_pool):
                running += weight
                if running >= target:
                    index = candidate_index
                    break
        selected.append(pool.pop(index))
        weight_pool.pop(index)

    return selected
