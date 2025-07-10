# 📈 Mutual Fund News Analyzer

The Mutual Fund News Analyzer is a smart web application that combines live financial news, Gemini AI-powered analysis, and NAV-based insights to help investors make better decisions. It supports both **single fund evaluation** and **comparative analysis** of two mutual funds across India, Europe, and the US.

---

## 🧠 Features

- 🔎 **Gemini AI-based Fund Analysis** from live news
- 📊 **NAV Performance Charts** over 1mo, 3mo, 6mo, 1y
- 🧮 **Return Distribution and Volatility Metrics**
- 🏅 **Performance Badges** like “🏆 Top Gainer 3M”, “🔻 High Risk”, “🔥 Trending in News”
- ⚖️ **Compare Two Funds Side-by-Side**
- 🧾 **Download PDF Reports** with insights
- 📚 **Sentiment Detection** and **Sector Impact**
- 🤖 **(Optional)** Q&A chatbot with contextual finance replies

---

## ⚙️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **AI Integration**: Google Gemini API (Generative AI)
- **Visualization**: Matplotlib
- **Data**: JSON-based NAV data (`mf.json`)
- **Others**: FPDF (PDF generation), WordCloud, RSS (News Parsing)

---

## 📁 Folder Structure

```
project/
│
├── app.py # Main Streamlit application
├── mf.json # Mutual fund NAV data
├── README.md # This file
├── requirements.txt # All required Python packages
└── .gitignore # Git ignored files
```

---

## 🔧 Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-username/MutualFundAnalyzer.git
cd MutualFundAnalyzer
```


2. **Create a virtual environment**
```
python -m venv .venv
source .venv/bin/activate  # For Linux/macOS
.venv\Scripts\activate     # For Windows
```
4. Install dependencies
```
pip install -r requirements.txt
```
5. Set your Gemini API Key
```
Edit app.py and replace:
genai.configure(api_key="your_actual_key")
```
6. Run the app
```
streamlit run app.py
```
