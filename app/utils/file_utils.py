import os
import uuid

MAX_FILE_SIZE = 50 * 1024 * 1024
UPLOAD_DIR = "/tmp/telegram_uploads"


def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_temp_path(original_filename: str) -> str:
    ensure_upload_dir()
    ext = os.path.splitext(original_filename)[1] or ""
    return os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")


def cleanup_temp(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
