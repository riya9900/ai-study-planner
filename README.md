# 📚 AI Study Planner Agent

An interactive web application that helps students and lifelong learners build personalized, realistic study plans using an AI Agent equipped with intelligent calculation tools.

## 🚀 Tech Stack
- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **AI / LLM:** Google Gemini API (`google-genai`)
- **Agent Logic:** Python with custom scheduling & pacing tools

## 🛠️ Setup Instructions (Local)
1. **Clone the repository** (or navigate to project folder)
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up your environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
5. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

