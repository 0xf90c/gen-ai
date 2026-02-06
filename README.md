# Data Insights App

Streamlit + Python agent with function calling.

Features:
- Chat over database
- Data never fully sent to LLM
- Business dashboard
- Tool calling
- Support ticket creation
- Safety (SELECT only)

Run:
pip install -r requirements.txt
python seed_data.py
export OPENAI_API_KEY=xxx
export GITHUB_TOKEN=xxx
export GITHUB_REPO=username/repo
streamlit run app.py