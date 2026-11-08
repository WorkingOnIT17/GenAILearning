import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Sample descriptions for instant testing
SAMPLE_MOVIES = {
    "Inception (2010)": (
        "Inception is a 2010 mind-bending science fiction thriller directed and written by Christopher Nolan. "
        "The film stars Leonardo DiCaprio as Dom Cobb, a skilled professional thief who extracts valuable secrets "
        "from deep within the subconscious during the dream state. Cobb is offered a chance to have his criminal history "
        "erased in exchange for an almost impossible task: inception—planting an idea into the subconscious of a CEO "
        "named Robert Fischer (Cillian Murphy). The ensemble cast includes Joseph Gordon-Levitt as Arthur, "
        "Elliot Page as Ariadne, Tom Hardy as Eames, and Ken Watanabe as Saito. The film explores grief, memory, "
        "guilt, and the thin boundary between reality and dream illusions."
    ),
    "The Dark Knight (2008)": (
        "The Dark Knight, directed by Christopher Nolan and released in 2008, is a gritty superhero neo-noir action film. "
        "Christian Bale stars as Bruce Wayne / Batman, who forms an uneasy alliance with police lieutenant James Gordon "
        "(Gary Oldman) and newly elected district attorney Harvey Dent (Aaron Eckhart) to dismantle organized crime in Gotham City. "
        "Their efforts are disrupted by a sadistic criminal mastermind known as the Joker (Heath Ledger in an Oscar-winning role), "
        "who seeks to undermine Batman's moral code and plunge the entire city into anarchy and nihilism. Maggie Gyllenhaal plays "
        "Rachel Dawes, and Michael Caine portrays Alfred Pennyworth. Major themes include order versus chaos, morality, "
        "heroism, sacrifice, and the corruption of virtue."
    ),
    "Parasite (2019)": (
        "Parasite is a 2019 South Korean black comedy psychological thriller directed by Bong Joon-ho. "
        "The movie stars Song Kang-ho as Kim Ki-taek, the patriarch of a destitute family living in a cramped semi-basement apartment. "
        "His son Ki-woo (Choi Woo-shik) secures a job as an English tutor for the daughter of the wealthy Park family (Lee Sun-kyun and "
        "Cho Yeo-jeong). One by one, the Kim family members use cunning deception to infiltrate the lavish Park household as unrelated "
        "highly-qualified domestic workers. Things take a dark and unexpected turn when an unexpected secret beneath the house is revealed. "
        "The story examines class conflict, wealth inequality, social mobility, and greed."
    )
}

# Core analysis prompt template (exact layout and instructions as main.py)
ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [(
        "system",
        """You are an expert film analyst. 
        Extract key metadata from the provided movie description and format it into a clean, human-readable summary.

        Use the following exact layout:

        **Title:** [Movie title or 'Not specified']
        **Release Year:** [Year or 'Not specified']
        **Director:** [Director name or 'Not specified']
        **Genre(s):** [Comma-separated genres]
        **Key Cast & Characters:**
        - [Actor name / Character role]
        **One-Sentence Summary:** [Concise high-level plot summary]
        **Core Themes:** [Comma-separated list of major themes]

        Rules:
        - Only include information stated or directly implied in the text.
        - Do not invent details; use 'Not specified' if missing.
        - Keep the response direct and free of conversational filler."""
    ),
    (
        "human",
        """Analyze this movie description:
        \"\"\"
        {movie_description}
        \"\"\""""
    )]
)

def analyze_movie_description(movie_description: str, api_key: str = None) -> str:
    """Core CineSage processing pipeline reproducing main.py."""
    kwargs = {
        "model": "gemini-3.5-flash-lite",
        "max_tokens": 1024
    }
    if api_key:
        kwargs["google_api_key"] = api_key
    elif os.getenv("GEMINI_API_KEY"):
        kwargs["google_api_key"] = os.getenv("GEMINI_API_KEY")
    elif os.getenv("GOOGLE_API_KEY"):
        kwargs["google_api_key"] = os.getenv("GOOGLE_API_KEY")

    model = ChatGoogleGenerativeAI(**kwargs)
    final_prompt = ANALYSIS_PROMPT.invoke({"movie_description": movie_description})
    response = model.invoke(final_prompt)

    # Clean string extraction handling both str and list content types
    if isinstance(response.content, str):
        clean_text = response.content.strip()
    elif isinstance(response.content, list):
        clean_text = "".join(
            part if isinstance(part, str) else part.get("text", "") 
            for part in response.content
        ).strip()
    else:
        clean_text = str(response.content).strip()

    return clean_text

def parse_metadata(markdown_text: str) -> dict:
    """Parse the structured layout into a dictionary for enriched dashboard display."""
    data = {
        "title": "Not specified",
        "year": "Not specified",
        "director": "Not specified",
        "genres": [],
        "cast": [],
        "summary": "Not specified",
        "themes": []
    }

    # Match Title
    title_match = re.search(r"\*\*Title:\*\*\s*(.+)", markdown_text, re.IGNORECASE)
    if title_match:
        data["title"] = title_match.group(1).strip()

    # Match Year
    year_match = re.search(r"\*\*Release Year:\*\*\s*(.+)", markdown_text, re.IGNORECASE)
    if year_match:
        data["year"] = year_match.group(1).strip()

    # Match Director
    dir_match = re.search(r"\*\*Director:\*\*\s*(.+)", markdown_text, re.IGNORECASE)
    if dir_match:
        data["director"] = dir_match.group(1).strip()

    # Match Genres
    genre_match = re.search(r"\*\*Genre\(s\):\*\*\s*(.+)", markdown_text, re.IGNORECASE)
    if genre_match:
        raw_genres = genre_match.group(1).strip()
        data["genres"] = [g.strip() for g in raw_genres.split(",") if g.strip() and g.strip().lower() != "not specified"]

    # Match Cast
    cast_match = re.search(r"\*\*Key Cast & Characters:\*\*(.*?)(?=\*\*One-Sentence Summary:\*\*|$)", markdown_text, re.DOTALL | re.IGNORECASE)
    if cast_match:
        raw_cast = cast_match.group(1).strip().splitlines()
        for line in raw_cast:
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                cleaned = line.lstrip("-* ").strip()
                if cleaned and cleaned.lower() != "not specified":
                    data["cast"].append(cleaned)

    # Match Summary
    sum_match = re.search(r"\*\*One-Sentence Summary:\*\*\s*(.+?)(?=\*\*Core Themes:\*\*|$)", markdown_text, re.DOTALL | re.IGNORECASE)
    if sum_match:
        data["summary"] = sum_match.group(1).strip()

    # Match Themes
    themes_match = re.search(r"\*\*Core Themes:\*\*\s*(.+)", markdown_text, re.DOTALL | re.IGNORECASE)
    if themes_match:
        raw_themes = themes_match.group(1).strip()
        data["themes"] = [t.strip() for t in raw_themes.split(",") if t.strip() and t.strip().lower() != "not specified"]

    return data

def main():
    # Page configuration
    st.set_page_config(
        page_title="CineSage | AI Film Analyst",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom Styling for Cinema Theme
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.3rem;
            font-weight: 700;
            background: linear-gradient(90deg, #E50914, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            color: #888888;
            font-size: 1.05rem;
            margin-bottom: 1.8rem;
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .metric-label {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #FFA500;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.15rem;
            font-weight: 600;
            color: #FAFAFA;
        }
        .genre-pill {
            display: inline-block;
            background: rgba(229, 9, 20, 0.18);
            border: 1px solid rgba(229, 9, 20, 0.5);
            color: #FF6B6B;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .theme-pill {
            display: inline-block;
            background: rgba(255, 165, 0, 0.15);
            border: 1px solid rgba(255, 165, 0, 0.4);
            color: #FFC04D;
            padding: 3px 12px;
            border-radius: 16px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .summary-box {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #E50914;
            padding: 14px 18px;
            border-radius: 0 8px 8px 0;
            font-size: 1.05rem;
            line-height: 1.5;
            font-style: italic;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "movie_input" not in st.session_state:
        st.session_state["movie_input"] = ""
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🎬 CineSage")
        st.caption("AI-Powered Film Metadata & Synopsis Intelligence")

        st.markdown("---")
        st.subheader("⚙️ Configuration")
        st.write("**Model:** `gemini-3.5-flash-lite`")
        st.write("**Max Tokens:** `1024`")

        env_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_api_key:
            st.success("API Key detected from environment")
            user_key = st.text_input("Override API Key (Optional)", type="password", placeholder="Leave blank to use .env")
            active_api_key = user_key.strip() if user_key.strip() else env_api_key
        else:
            st.warning("⚠️ No API Key found in `.env`")
            active_api_key = st.text_input("Enter Gemini API Key", type="password", placeholder="AIzaSy...")

        st.markdown("---")
        st.subheader("📚 Quick Samples")
        selected_sample = st.selectbox(
            "Load an example movie paragraph:",
            ["None"] + list(SAMPLE_MOVIES.keys()),
            index=0
        )
        if selected_sample != "None":
            if st.button("Load This Sample", use_container_width=True):
                st.session_state["movie_input"] = SAMPLE_MOVIES[selected_sample]
                st.rerun()

        st.markdown("---")
        st.markdown("""
        **About CineSage**  
        CineSage takes an unformatted natural language movie synopsis, extracts core metadata, identifies cast, and summarizes the plot and themes using Gemini 3.5.
        """)

    # --- MAIN CONTENT ---
    st.markdown('<div class="main-header">CineSage Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract structured film metadata, themes, and key cast members from raw text descriptions</div>', unsafe_allow_html=True)

    col_input, col_info = st.columns([3, 1])

    with col_info:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border-left: 3px solid #FFA500; padding: 12px; border-radius: 4px; font-size: 0.9rem;">
            <strong>💡 Tip:</strong> Paste a synopsis from IMDb, Wikipedia, or your own notes. CineSage will extract:
            <ul style="margin-top: 6px; padding-left: 18px;">
                <li>Title & Release Year</li>
                <li>Director & Genres</li>
                <li>Key Cast & Roles</li>
                <li>Single-Sentence Synopsis</li>
                <li>Core Themes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_input:
        movie_text = st.text_area(
            label="Movie Description / Synopsis Paragraph",
            value=st.session_state["movie_input"],
            height=180,
            placeholder="Paste a movie description, synopsis, or review paragraph here..."
        )
        st.session_state["movie_input"] = movie_text

    # Action buttons
    btn_col1, btn_col2, _ = st.columns([1.5, 1, 3])

    with btn_col1:
        analyze_clicked = st.button("🚀 Analyze Movie", type="primary", use_container_width=True)

    with btn_col2:
        if st.button("🧹 Clear Input", use_container_width=True):
            st.session_state["movie_input"] = ""
            st.session_state["analysis_result"] = None
            st.rerun()

    # Execution
    if analyze_clicked:
        if not movie_text.strip():
            st.error("Please enter a movie description paragraph first.")
        elif not active_api_key:
            st.error("Google/Gemini API key is required. Please set GEMINI_API_KEY in your .env or provide it in the sidebar.")
        else:
            with st.spinner("Analyzing movie description with Gemini 3.5 Flash Lite..."):
                try:
                    result_text = analyze_movie_description(movie_text.strip(), api_key=active_api_key)
                    st.session_state["analysis_result"] = result_text
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

    # Display Results
    if st.session_state.get("analysis_result"):
        result_text = st.session_state["analysis_result"]
        parsed = parse_metadata(result_text)

        st.markdown("---")
        st.subheader("📊 Analysis Results")

        tab_visual, tab_markdown, tab_raw = st.tabs(["✨ Structured View", "📝 Formatted Markdown", "📋 Raw Output & Copy"])

        with tab_visual:
            # Top Metrics Row
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Title</div>
                    <div class="metric-value">{parsed['title']}</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Release Year</div>
                    <div class="metric-value">{parsed['year']}</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Director</div>
                    <div class="metric-value">{parsed['director']}</div>
                </div>
                """, unsafe_allow_html=True)

            # Genres
            st.markdown("**Genres:**")
            if parsed["genres"]:
                genres_html = "".join([f'<span class="genre-pill">{g}</span>' for g in parsed["genres"]])
                st.markdown(genres_html, unsafe_allow_html=True)
            else:
                st.write("Not specified")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # One-sentence summary
            st.markdown("**One-Sentence Summary:**")
            st.markdown(f'<div class="summary-box">"{parsed["summary"]}"</div>', unsafe_allow_html=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # Cast & Themes columns
            cast_col, themes_col = st.columns(2)

            with cast_col:
                st.markdown("**Key Cast & Characters:**")
                if parsed["cast"]:
                    for member in parsed["cast"]:
                        st.markdown(f"- **{member}**")
                else:
                    st.write("Not specified")

            with themes_col:
                st.markdown("**Core Themes:**")
                if parsed["themes"]:
                    themes_html = "".join([f'<span class="theme-pill">{t}</span>' for t in parsed["themes"]])
                    st.markdown(themes_html, unsafe_allow_html=True)
                else:
                    st.write("Not specified")

        with tab_markdown:
            st.markdown(result_text)

        with tab_raw:
            st.code(result_text, language="markdown")
            st.download_button(
                label="💾 Download Summary (.txt)",
                data=result_text,
                file_name=f"{parsed['title'].replace(' ', '_').lower()}_summary.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
