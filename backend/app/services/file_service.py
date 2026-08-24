"""
File Service

Handles secure storage of uploaded source files:
- extension/language validation
- file size limits
- safe/randomized filenames (never trust user-supplied names for storage)
- SHA-256 hashing for duplicate detection

Uploaded source code is only ever read as text and parsed by the AST
engine. It is never executed.
"""
import hashlib
import os
import re
import uuid

from fastapi import UploadFile

from app.config import settings

ALLOWED_EXTENSIONS = {
    ".py": "python",
    # Placeholders for future language support (see ast_engine.parser registry).
    # ".java": "java", ".c": "c", ".cpp": "cpp", ".js": "javascript",
}

MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


class FileValidationError(Exception):
    pass


def _safe_stub(original_name: str) -> str:
    stub = re.sub(r"[^a-zA-Z0-9_.-]", "_", original_name)[:60]
    return stub or "upload"


def detect_language(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file extension '{ext}'. Supported: {list(ALLOWED_EXTENSIONS.keys())}"
        )
    return ALLOWED_EXTENSIONS[ext]


async def save_upload(file: UploadFile, user_id: int) -> dict:
    if not file.filename:
        raise FileValidationError("No filename provided.")

    language = detect_language(file.filename)

    contents = await file.read()
    if len(contents) == 0:
        raise FileValidationError("Uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError(
            f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB."
        )

    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FileValidationError("File is not valid UTF-8 text source code.") from exc

    # Validate it actually parses as source code for the declared language,
    # so obviously-invalid or malicious binary content is rejected early.
    from app.ast_engine.parser import parse_source, CodeParseError

    try:
        parse_source(text, language)
    except CodeParseError as exc:
        raise FileValidationError(f"Invalid source code: {exc}") from exc

    code_hash = hashlib.sha256(contents).hexdigest()
    stored_name = f"user{user_id}_{uuid.uuid4().hex}_{_safe_stub(file.filename)}"
    user_dir = os.path.join(settings.UPLOAD_DIRECTORY, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    stored_path = os.path.join(user_dir, stored_name)

    with open(stored_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {
        "filename": file.filename,
        "stored_path": stored_path,
        "language": language,
        "file_size": len(contents),
        "code_hash": code_hash,
    }


def read_source(stored_path: str) -> str:
    if not os.path.exists(stored_path):
        raise FileValidationError("Stored source file could not be found.")
    with open(stored_path, "r", encoding="utf-8") as f:
        return f.read()
