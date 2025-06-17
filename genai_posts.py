from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel


class GeneratedPost(BaseModel):
    post_content: str
    image_recommendation: str | None = None


def get_generated_content(
    api_key: str, model: str, posts: list[dict]
) -> list[GeneratedPost]:
    gemini_client = genai.Client(api_key=api_key)

    # set system instruction
    system_instruction: str = """
    You are a helpful AI assistant that generates engaging LinkedIn posts based on the provided content.
    Your task is to create a post that is concise, engaging, and relevant to the content provided.
    The post should be suitable for a professional audience on LinkedIn.
    """

    # Prepare the prompt for the model
    prompt: str = f"""
    Generate 10 different LinkedIn posts based on the following content.
    Each post should be concise, engaging, and suitable for a professional audience.
    If there more than one language being used, provide posts in each language.
    Stick to the tone, style and average length of the provided posts.
    If an image is recommended for the post, include a brief description of the image as a prompt to input to the image generation model.
    Here are some linkedin posts for this user:
    {"".join(f"{i}. {post['text']}" + (f"\n Image with the post: {Image.open(post['image_path'])}" if post['image_path'] else "") for i, post in enumerate(posts, start=1))}
    """

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[GeneratedPost],
            "system_instruction": system_instruction,
            "thinking_config": types.ThinkingConfig(thinking_budget=1024),
        },
    )

    if not response or not response.text or not response.parsed:
        raise ValueError("No response or parsed content received from the model.")

    generated_posts: list[GeneratedPost] = response.parsed
    return generated_posts
