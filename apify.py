import json
import os

import requests
from apify_client import ApifyClient

api_key: str = "apify_api_80oNCjYGXp9VjbVHpdywxAlMGLClkh2NUL3b"


def get_image_from_post(post: dict) -> str | None:
    """
    Extracts the image URL from a LinkedIn post if it exists and saves it to a file.

    Args:
        post (dict): The LinkedIn post data containing media information.
    Returns:
        str | None: The path to the saved image file if an image exists, otherwise None.
    """
    image_url: str | None = None

    if (
        "media" in post
        and post["media"]["type"] == "image"
        and "images" in post["media"]
        and len(post["media"]["images"]) > 0
    ):
        image_url: str | None = post["media"]["images"][0].get("url", None)

    if image_url:
        os.makedirs("images", exist_ok=True)
        with open(f"images/{post['urn']}.jpg", "wb") as f:
            response = requests.get(image_url)
            f.write(response.content)
    else:
        print(f"No image found for post {post['urn']}")

    return f"images/{post['urn']}.jpg" if image_url else None


def get_posts(
    linkedin_username: str, limit: int, api_key: str, load_cache: bool = True
) -> list[dict]:
    if load_cache:
        print("Loading posts from cache...")
        # Check if the posts are already cached
        cache_file = f"posts_cache/{linkedin_username}_posts.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return json.load(f)

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

    # get the image for each post (if exists)
    for post in posts:
        image_path: str | None = get_image_from_post(post)
        post["image_path"] = image_path if image_path else None

    # write the posts to a file
    os.makedirs("posts_cache", exist_ok=True)

    with open(f"posts_cache/{linkedin_username}_posts.json", "w") as f:
        json.dump(posts, f, indent=4)

    return posts
