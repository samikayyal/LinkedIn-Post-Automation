from apify_client import ApifyClient

from utils.supabase_utils import get_user_posts, write_user_posts

api_key: str = "apify_api_80oNCjYGXp9VjbVHpdywxAlMGLClkh2NUL3b"


def get_posts(
    linkedin_username: str,
    limit: int,
    apify_key: str,
    load_cache: bool = True,
) -> list[dict]:
    if load_cache:
        print("Loading posts from supabase cache...")
        posts: list[dict] = get_user_posts(linkedin_username, limit=limit)
        if posts:
            return posts

    print("Fetching posts from Apify...")
    client = ApifyClient(apify_key)

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
    write_user_posts(
        linkedin_username=linkedin_username,
        posts=posts,
    )

    return posts
