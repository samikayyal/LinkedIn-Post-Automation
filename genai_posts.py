from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel


class GeneratedPost(BaseModel):
    post_content: str
    image_recommendation: str | None = None


def get_generated_content(
    api_key: str, model: str, posts: list[dict]
) -> tuple[list[GeneratedPost], Any]:
    print("Generating content based on provided posts...")
    gemini_client = genai.Client(api_key=api_key)
    num_posts = len(posts)

    # Prepare the prompt for the model
    prompt: str = f"""
    Your task is to generate {num_posts} distinct LinkedIn posts based on the provided "Core Content".
    You must carefully analyze the "Style Examples" to understand the user's tone, voice, typical length, and use of hashtags and emojis. Your generations must emulate this style.

    **Instructions:**
    1.  **Analyze Tone & Style:** Study the provided examples to capture the user's unique voice.
    2.  **Generate Posts:** Create {num_posts} variations based on the "Core Content". Each post must be concise, engaging, and professional.
    3.  **Multi-language:** If the examples or content use multiple languages, generate posts in each of those languages.
    4.  **Image Prompts:** If a post would be enhanced by an image, provide a detailed, descriptive prompt for an image generation model (e.g., "A photorealistic image of a diverse team collaborating around a futuristic whiteboard..."). If no image is needed, leave it null.
    5.  **Output Format:** Your final output MUST be a valid JSON array of objects, strictly adhering to the provided schema. In the post content, make sure to properly format correctly, including any necessary new lines, bullet points, emojis, etc.. .

    ---
    **Core Content to Write About:**
    Generate post ideas based on your interpretaion of the user's style and the provided content.
    ---
    **Style Examples from User's Past Posts:**
    {"\n".join([f"Post {i}:\n {post['text']}" for i, post in enumerate(posts, start=1)])}
    ---
    """

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[GeneratedPost],
            "thinking_config": types.ThinkingConfig(thinking_budget=2048),
        },
    )

    if not response or not response.text or not response.parsed:
        raise ValueError("No response or parsed content received from the model.")

    generated_posts: list[GeneratedPost] = response.parsed
    return generated_posts, response
