import os

import dotenv

from apify import get_posts


def main():
    dotenv.load_dotenv()

    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    APIFY_API_KEY: str | None = os.getenv("APIFY_API_KEY")

    if not GEMINI_API_KEY or not APIFY_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY and APIFY_API_KEY must be set in the environment variables."
        )

    linkedin_username: str = input("Enter LinkedIn username: ")
    posts: list[dict] = get_posts(
        linkedin_username=linkedin_username,
        limit=10,
        api_key=APIFY_API_KEY,
        load_cache=True,
    )


"""
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

response = gemini_client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Hi there! What can you do?",
)

with open("response.md", "w") as f:
    f.write(response.text)
"""
