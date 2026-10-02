"""Payload type detection without changing authoritative path spelling."""


def is_mra(path):
    return path.lower().endswith(".mra")
