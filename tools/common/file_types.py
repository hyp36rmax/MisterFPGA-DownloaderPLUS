"""Payload type detection without changing authoritative path spelling."""


def is_mra(path):
    return path.lower().endswith(".mra")


def alternative_directory(path):
    """Recognize upstream alternative directory spellings without renaming them."""
    return next((part for part in path.split("/") if part in {"_alternatives", "_alternative"}), None)
