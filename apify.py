import json
import os

from apify_client import ApifyClient

api_key: str = "apify_api_80oNCjYGXp9VjbVHpdywxAlMGLClkh2NUL3b"


def get_posts(
    linkedin_username: str, limit: int, api_key: str, load_cache: bool = True
) -> list[dict]:
    if load_cache:
        # Check if the posts are already cached
        cache_file = f"posts_cache/{linkedin_username}_posts.json"
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return json.load(f)

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

    with open(f"posts_cache/{linkedin_username}_posts.json", "w") as f:
        json.dump(posts, f, indent=4)

    return posts
