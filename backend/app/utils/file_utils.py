import os
from pathlib import Path

def ensure_dir(directory: str) -> None:
    """Ensure that a directory exists, create it if it does not."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_file_extension(filename: str) -> str:
    """Returns the file extension in lowercase."""
    return os.path.splitext(filename)[1].lower()
