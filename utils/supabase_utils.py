import json
import os
from datetime import datetime

import dotenv
import streamlit as st
from supabase.client import Client, create_client


def get_user_posts(linkedin_username: str, limit: int) -> list[dict]:
    """
    Fetches user posts from Supabase based on the hashed LinkedIn username.

    Args:
        hashed_linkedin_username (str): The hashed LinkedIn username.

    Returns:
        list[dict]: A list of posts for the user.
    """
    supabase_client: Client | None = st.session_state.get("supabase_client")
    if not supabase_client or not isinstance(supabase_client, Client):
        raise ValueError(
            "Supabase client is not initialized in session state. Or not a valid Client instance."
        )

    response = (
        supabase_client.table("user_linkedin_posts")
        .select("*")
        .eq("username", linkedin_username)
        .limit(limit)
        .execute()
    )

    return response.data


def write_user_posts(linkedin_username: str, posts: list[dict]) -> None:
    """
    Writes user posts to Supabase.

    Args:
        linkedin_username (str): The LinkedIn username.
        posts (list[dict]): A list of posts to write.

    Returns:
        None
    """
    supabase_client: Client | None = st.session_state.get("supabase_client")
    if not supabase_client or not isinstance(supabase_client, Client):
        raise ValueError(
            "Supabase client is not initialized in session state. Or not a valid Client instance."
        )

    for post in posts:
        post_data: dict = {
            "urn": post["urn"],
            "username": linkedin_username,
            "text": post["text"],
            "full_urn": post["full_urn"],
            "posted_at": datetime.fromisoformat(post["posted_at"]["date"]).isoformat(),
            "url": post["url"],
            "author_first_name": post["author"].get("first_name", ""),
            "author_last_name": post["author"].get("last_name", ""),
            "author_profile_url": post["author"].get("profile_url", ""),
            "num_reactions": int(post.get("stats", 0).get("total_reactions", 0)),
        }

        # Use upsert to only insert new posts and ignore duplicates to not overwrite existing ones
        response = (  # noqa: F841
            supabase_client.table("user_linkedin_posts").upsert(
                post_data, ignore_duplicates=True
            )
        ).execute()


if __name__ == "__main__":
    # Example usage
    linkedin_username: str = "maheralkhadra"

    # Load old posts from cache and upload them here
    # This is just a placeholder, replace with actual logic to load posts
    # with open(f"posts_cache/{hash_username(linkedin_username)}_posts.json", "r") as f:
    #     cached_posts = json.load(f)

    # write_user_posts(linkedin_username, cached_posts)

    # posts: list[dict] = get_user_posts(linkedin_username, 10)
    # print(posts)
