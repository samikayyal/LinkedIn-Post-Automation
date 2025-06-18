import hashlib
import json
import os

from apify_client import ApifyClient

api_key: str = "apify_api_80oNCjYGXp9VjbVHpdywxAlMGLClkh2NUL3b"


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


def get_posts(
    linkedin_username: str, limit: int, api_key: str, load_cache: bool = True
) -> list[dict]:
    if load_cache:
        print("Loading posts from cache...")
        # Check if the posts are already cached
        cache_file = f"posts_cache/{hash_username(linkedin_username)}_posts.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
                if len(data) >= limit:
                    return data

    print("Fetching posts from Apify...")
    client = ApifyClient(api_key)

    # Set up the run input (parameters for the actor)
    run_input: dict = {"username": linkedin_username, "limit": limit, "page_number": 1}

    # Start the actor
    run: dict | None = client.actor("apimaestro/linkedin-profile-posts").call(
        run_input=run_input
    )
    if run is None:
        raise ValueError("Run did not return any results.")

    # get the posts from the run result
    if "defaultDatasetId" not in run:
        raise ValueError("No default dataset found in the run result.")

    posts: list[dict] = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        posts.append(item)

    # write the posts to a file
    os.makedirs("posts_cache", exist_ok=True)

    with open(f"posts_cache/{hash_username(linkedin_username)}_posts.json", "w") as f:
        json.dump(posts, f, indent=4)

    return posts
