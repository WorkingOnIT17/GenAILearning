# CineSage 🎬

CineSage is an AI film analysis tool that extracts structured metadata, key cast members, themes, and high-level summaries from natural language movie synopsis paragraphs using Google Gemini.

---

## Features

- **Metadata Extraction:** Title, Release Year, Director, and Genres.
- **Key Cast & Roles:** Identifies main actors and their corresponding character roles.
- **Core Themes & Synopsis:** Delivers a concise one-sentence plot overview and core thematic breakdown.
- **Multiple Output Views:** Structured cards, formatted Markdown, and raw text export.

---

## Getting Started

### 1. Environment Setup

Ensure you have your Gemini API key in your `.env` file at the project root:

```env
GEMINI_API_KEY="your_api_key_here"
```

### 2. Install Dependencies

Activate your virtual environment and install the required packages:

```bash
pip install -r requirements.txt
```

---

## Running CineSage

### 🚀 Streamlit Dashboard (UI)

To launch the interactive web dashboard:

```bash
streamlit run CineSage/app.py
```

Features included in the dashboard:
- Interactive text area for custom movie descriptions.
- Quick one-click sample loader (Inception, The Dark Knight, Parasite).
- Structured visual cards, badges, and formatted tabs.
- Downloadable summary reports.
- Optional sidebar API key override.

### 💻 CLI Mode

To run the original command-line interface:

```bash
python CineSage/main.py
```
