import os
from typing import Dict, List, Optional, Tuple

import dotenv
import streamlit as st
from supabase.client import Client, create_client

from apify_posts import get_posts
from genai_posts import get_generated_content

# --- Constants ---
PAGE_CONFIG: dict[str, str] = {
    "page_title": "LinkedIn Post Automator",
    "layout": "wide",
    "page_icon": "🤖",
    "initial_sidebar_state": "collapsed",
}
GEMINI_MODEL: str = "gemini-2.5-flash-preview-05-20"
POST_FETCH_LIMIT: int = 10
CSS_FILE: str = "style.css"


def is_arabic(text: str) -> bool:
    """Checks if a string contains Arabic characters."""
    if not text:
        return False
    return any("\u0600" <= char <= "\u06ff" for char in text)


def load_api_keys() -> Tuple[Optional[str], Optional[str]]:
    """Loads API keys from .env file and returns them."""
    dotenv.load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    apify_api_key = os.getenv("APIFY_API_KEY")
    return gemini_api_key, apify_api_key


# --- UI Rendering Functions ---
def render_header():
    """Renders the main application header."""
    st.markdown(
        """
        <div class="header-container">
            <h1 class="header-title">LinkedIn Post Automator 🤖</h1>
            <p class="header-subtitle">Generate engaging content by analyzing existing posts with AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_input_form():
    """Renders the input form for the LinkedIn username."""
    with st.form(key="generation_form"):
        linkedin_username = st.text_input(
            "🔍 Enter LinkedIn Profile Username",
            placeholder="The part after linkedin.com/in/",
            help="The part after linkedin.com/in/",
            key="linkedin_username_input",
        )
        submitted = st.form_submit_button("✨ Generate Posts")

    if submitted:
        if not linkedin_username.strip():
            st.error("⚠️ **Username cannot be empty.** Please enter a valid username.")
            st.stop()
        # Trigger the generation process
        st.session_state.username = linkedin_username.strip()
        handle_generation_process()


def render_results():
    """Displays the generated content, metadata, and any errors."""
    if st.session_state.error:
        st.error(st.session_state.error)
        return

    content = st.session_state.generated_content
    response = st.session_state.api_response  # noqa: F841

    if content:
        st.markdown("---")
        st.success(f"🎉 **Success!** Generated {len(content)} unique post ideas.")

        for i, post_item in enumerate(content, start=1):
            with st.expander(f"💡 **Post Idea #{i}**", expanded=True):
                # Use st.code for content with a built-in copy button
                if not is_arabic(post_item.post_content):
                    st.code(
                        post_item.post_content,
                        language="markdown",
                    )
                else:
                    st.markdown(
                        f'<div dir="rtl" style="text-align: right; white-space: pre-wrap; font-family: monospace;">{post_item.post_content}</div>',
                        unsafe_allow_html=True,
                    )

                if post_item.image_recommendation:
                    st.markdown(
                        f'<div class="image-recommendation">🎨 <strong>Image Suggestion:</strong> {post_item.image_recommendation}</div>',
                        unsafe_allow_html=True,
                    )


def render_footer():
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #6c757d; margin-top: 2rem; font-size: 0.9rem;">
            <p><strong>Pro Tips:</strong> Review and customize content before posting.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_generation_process():
    GEMINI_API_KEY, APIFY_API_KEY = load_api_keys()

    # Reset state for new generation
    st.session_state.generated_content = None
    st.session_state.api_response = None
    st.session_state.error = None

    progress_bar = st.progress(0, text="🚀 Starting generation...")

    try:
        # Fetch posts
        progress_bar.progress(
            10, text=f"🔍 Fetching posts for '{st.session_state.username}'..."
        )
        posts: List[Dict] = get_posts(
            linkedin_username=st.session_state.username,
            limit=POST_FETCH_LIMIT,
            apify_key=APIFY_API_KEY,  # type: ignore
        )

        if not posts:
            st.session_state.error = (
                f"📭 **No posts found for '{st.session_state.username}'.** "
                "Please check the username and ensure their posts are public."
            )
            progress_bar.empty()
            return

        progress_bar.progress(
            50, text=f"✅ Found {len(posts)} posts. Analyzing style..."
        )

        # Generate content
        generated_content, response = get_generated_content(
            api_key=GEMINI_API_KEY,  # type: ignore
            model=GEMINI_MODEL,
            posts=posts,
        )

        progress_bar.progress(90, text="✨ Finalizing content...")

        st.session_state.generated_content = generated_content
        st.session_state.api_response = response

        progress_bar.progress(100, text="✅ Generation Complete!")
        progress_bar.empty()

    except Exception as e:
        st.session_state.error = f"❌ **An unexpected error occurred:** {e}"
        progress_bar.empty()


def main():
    # ============= Supabase initialization =============
    dotenv.load_dotenv()
    url: str | None = os.getenv("SUPABASE_URL")
    key: str | None = os.getenv("SUPABASE_KEY")
    if not url or not key:
        print(
            "⚠️ **Missing Supabase URL or Key!** Please set `SUPABASE_URL` and `SUPABASE_KEY` in a `.env` file."
        )
        st.stop()
        return
    is_supabase_cache: bool = True
    supabase_client: Client = create_client(
        supabase_url=url,
        supabase_key=key,
    )

    # ============= Streamlit app initialization =============
    st.set_page_config(**PAGE_CONFIG)
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found at style.css. Please ensure it exists.")

    # Initialize session state
    defaults = {
        "generated_content": None,
        "api_response": None,
        "error": None,
        "username": "",
        "is_supabase_cache": is_supabase_cache,
        "supabase_client": supabase_client,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    render_header()

    gemini_key, apify_key = load_api_keys()
    if not gemini_key or not apify_key:
        print(
            "⚠️ **Missing API Keys!** Please set `GEMINI_API_KEY` and `APIFY_API_KEY` in a `.env` file."
        )
        st.stop()

    render_input_form()
    render_results()
    render_footer()


if __name__ == "__main__":
    main()
