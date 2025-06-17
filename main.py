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

    generated_content, response = get_generated_content(
        api_key=GEMINI_API_KEY, model="gemini-2.5-flash-preview-05-20", posts=posts
    )

    with open("response.md", "w", encoding="utf-8") as f:
        f.write("# Response Details\n\n")
        f.write(f"**Usage Metadata:** {response.usage_metadata}\n\n")

        f.write("**Generated Posts:**\n\n")
        for i, post in enumerate(generated_content, start=1):
            f.write(f"## Post {i}\n\n")
            f.write(f"{post.post_content}\n\n")
            if post.image_recommendation:
                f.write(f"{post.image_recommendation}\n\n")
            else:
                f.write("No image recommendation.\n\n")

    return generated_content, response


if __name__ == "__main__":
    linkedin_username: str = "maheralkhadra"
    main(linkedin_username=linkedin_username)
