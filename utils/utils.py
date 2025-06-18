import hashlib


def hash_username(username: str) -> str:
    """
    Fetches the user hash for a LinkedIn profile.

    Args:
        username (str): The LinkedIn username or profile URL.

    Returns:
        str | None: The user hash if found, otherwise None.
    """

    # Convert the username to bytes.
    username_bytes = username.encode("utf-8")

    # Create a sha256 hash object.
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the username.
    sha256_hash.update(username_bytes)

    # Get the hexadecimal representation of the hash.
    hex_digest = sha256_hash.hexdigest()

    return hex_digest
