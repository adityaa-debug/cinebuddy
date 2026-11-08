import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="CineBuddy", page_icon="🎬", layout="centered")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .title {
        text-align: center; font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(90deg, #ff512f, #dd2476);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { text-align: center; opacity: 0.7; margin-bottom: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

# ---------- Sidebar ----------
with st.sidebar:
    st.header("🎛️ Your taste")
    genres = st.multiselect(
        "Favourite genres",
        ["Action", "Comedy", "Drama", "Thriller", "Romance", "Horror",
         "Sci-Fi", "Animation", "Crime", "Fantasy"],
    )
    mood = st.selectbox(
        "Mood", ["Any", "Happy", "Relaxed", "Excited", "Sad", "Romantic", "Thoughtful"]
    )
    language = st.selectbox(
        "Movie language",
        ["Any", "English", "Hindi", "Tamil", "Telugu", "Kannada", "Malayalam", "Korean"],
    )
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Built with Python, Streamlit and the Gemini API")

SYSTEM_PROMPT = f"""You are CineBuddy, a friendly movie suggestion assistant.
Ask about the user's mood, favourite genres or movies they liked.
Suggest 3 movies at a time, each with the year and a one-line reason.
Keep answers short and avoid spoilers.
User preferences from the sidebar: genres = {', '.join(genres) or 'any'};
mood = {mood}; movie language = {language}."""

# ---------- Header ----------
st.markdown('<div class="title">🎬 CineBuddy</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Tell me your mood and I\'ll pick your next movie</div>',
    unsafe_allow_html=True,
)

# ---------- Starter buttons (only when chat is empty) ----------
if not st.session_state.messages:
    st.write("Try one of these:")
    col1, col2, col3 = st.columns(3)
    if col1.button("😂 Funny movie for tonight"):
        st.session_state.pending = "Suggest a funny movie for tonight"
        st.rerun()
    if col2.button("🧠 Mind-bending thriller"):
        st.session_state.pending = "Suggest a mind-bending thriller"
        st.rerun()
    if col3.button("👨‍👩‍👧 Family movie night"):
        st.session_state.pending = "Suggest a movie for a family night"
        st.rerun()

# ---------- Chat history ----------
for msg in st.session_state.messages:
    avatar = "🎬" if msg["role"] == "assistant" else "🙂"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------- Input ----------
prompt = st.chat_input("Tell me your mood or a movie you loved...")
if st.session_state.pending:
    prompt = st.session_state.pending
    st.session_state.pending = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(prompt)

    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant", avatar="🎬"):
        with st.spinner("Picking movies for you..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=history,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                reply = response.text
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})