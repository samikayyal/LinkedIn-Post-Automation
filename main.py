import os

import dotenv

from apify import get_posts
from genai_posts import get_generated_content


def main(linkedin_username: str):
    dotenv.load_dotenv()

    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    APIFY_API_KEY: str | None = os.getenv("APIFY_API_KEY")

    if not GEMINI_API_KEY or not APIFY_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY and APIFY_API_KEY must be set in the environment variables."
        )

    posts: list[dict] = get_posts(
        linkedin_username=linkedin_username,
        limit=10,
        api_key=APIFY_API_KEY,
        load_cache=True,
    )

    generated_content = get_generated_content(
        api_key=GEMINI_API_KEY, model="gemini-2.0-flash", posts=posts
    )

    return generated_content


if __name__ == "__main__":
    linkedin_username: str = input("Enter LinkedIn username: ")
    main(linkedin_username=linkedin_username)
