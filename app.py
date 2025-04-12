import streamlit as st
import feedparser
import google.generativeai as genai
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from datetime import datetime, timedelta
import random
import json
import os
import numpy as np
import pandas as pd
from fpdf import FPDF

# Load NAV data from JSON file
nav_json_path = "mf.json"
if os.path.exists(nav_json_path):
    with open(nav_json_path, "r") as file:
        nav_data_all = json.load(file)
else:
    st.error("❌ NAV JSON file not found. Please make sure 'mf.json' is in the project folder.")
    nav_data_all = []

popular_funds = [
    # India
    "HDFC Top 100 Fund", "SBI Bluechip Fund", "Nippon India Growth Fund", "ICICI Prudential Bluechip Fund",
    "Axis Midcap Fund", "UTI Nifty Index Fund", "Kotak Flexicap Fund", "Aditya Birla Sun Life Tax Relief 96",
    "Mirae Asset Large Cap Fund", "Parag Parikh Flexi Cap Fund", "Tata Digital India Fund",
    "Motilal Oswal Nasdaq 100 ETF", "Quant Small Cap Fund", "Canara Robeco Bluechip Equity Fund",
    "Franklin India Prima Fund", "Edelweiss Mid Cap Fund", "Invesco India Contra Fund",
    "Baroda BNP Paribas Large Cap Fund", "DSP Tax Saver Fund", "Sundaram Large and Midcap Fund",
    # Europe
    "BlackRock Global Funds - European Equity Income Fund", "HSBC GIF Europe Equity Smaller Companies",
    "Fidelity European Growth Fund", "JPMorgan Europe Dynamic Fund", "Amundi Funds - Euroland Equity",
    "Schroder ISF European Large Cap", "DWS Invest European Equities", "Nordea European Equity Fund",
    "BNP Paribas Funds Europe Growth", "AXA WF Framlington Europe Opportunities",
    "Robeco European Stars Equities Fund", "Invesco Pan European Structured Equity Fund",
    "UBS European Opportunity Fund", "Allianz Europe Equity Growth Fund",
    "M&G European Strategic Value Fund", "KBC Equity Fund Europe", "Franklin Mutual European Fund",
    "Pictet European Sustainable Equities", "Candriam Equities L Europe Innovation",
    "Threadneedle European Select Fund",
    # US
    "Vanguard 500 Index Fund", "Fidelity Contrafund", "T. Rowe Price Blue Chip Growth Fund",
    "American Funds Growth Fund of America", "Schwab S&P 500 Index Fund",
    "BlackRock Equity Dividend Fund", "JPMorgan Large Cap Growth Fund", "Franklin Growth Fund",
    "Dodge & Cox Stock Fund", "Columbia Dividend Income Fund", "MFS Growth Fund",
    "Invesco QQQ Trust", "iShares Russell 1000 Growth ETF", "SPDR S&P 500 ETF Trust",
    "T. Rowe Price Dividend Growth Fund", "Vanguard Total Stock Market Index Fund",
    "Fidelity ZERO Large Cap Index Fund", "Principal Blue Chip Fund",
    "Janus Henderson Enterprise Fund", "Lord Abbett Growth Leaders Fund"
]

# Gemini setup
genai.configure(api_key="YOUR_KEY_HERE")
model = genai.GenerativeModel("models/gemini-1.5-pro")

# RSS feeds
RSS_FEEDS = [
    "https://finance.yahoo.com/rss/topstories",
    "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "https://www.livemint.com/rss/markets",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://feeds.feedburner.com/euronews/en/home",
    "https://www.politico.eu/rss/politics/",
    "https://europeannewsroom.com/feed",
    "https://www.france24.com/en/europe/rss",
    "https://euobserver.com/rss",
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "https://www.npr.org/rss/rss.php?id=1001",
    "http://feeds.reuters.com/Reuters/domesticNews",
    "https://www.cbsnews.com/latest/rss/main"
]

st.set_page_config(page_title="Mutual Fund Analyzer", layout="centered")

# Dark mode toggle
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        .css-1d391kg, .css-1v3fvcr {
            background-color: #333333;
            color: #ffffff;
        }
        .css-18e3th9 {
            background-color: #1e1e1e;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("📈 Mutual Fund News Analyzer")

fund_compare = st.checkbox("🔀 Compare Two Funds")
if fund_compare:
    selected_funds = st.multiselect("Select Two Funds:", popular_funds, max_selections=2)
else:
    selected_funds = [st.selectbox("Select Mutual Fund:", popular_funds)]

timeframe = st.selectbox("Select Timeframe for Chart:", ["1mo", "3mo", "6mo", "1y"])

def fetch_news(fund):
    keywords = fund.lower().split()
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            summary = getattr(entry, "summary", "")
            if any(word in entry.title.lower() or word in summary.lower() for word in keywords):
                articles.append(f"{entry.title}. {summary}")
    return articles

def generate_dummy_nav(days):
    base = 100.0
    return [round(base + random.uniform(-1, 1) + (i * random.uniform(-0.05, 0.05)), 2) for i in range(days)]

def plot_nav_chart(nav_data, title, period):
    if dark_mode: plt.style.use("dark_background")
    else: plt.style.use("default")
    dates = [datetime.now() - timedelta(days=len(nav_data) - i) for i in range(len(nav_data))]
    fig, ax = plt.subplots()
    ax.plot(dates, nav_data, color='teal')
    ax.set_title(f"{title} - NAV over {period}")
    ax.set_xlabel("Date")
    ax.set_ylabel("NAV")
    fig.autofmt_xdate()
    st.pyplot(fig)

def plot_returns_histogram(nav_data):
    returns = [j - i for i, j in zip(nav_data[:-1], nav_data[1:])]
    if dark_mode: plt.style.use("dark_background")
    else: plt.style.use("default")
    fig, ax = plt.subplots()
    ax.hist(returns, bins=20, color='purple', edgecolor='black')
    ax.set_title("Distribution of Daily Returns")
    ax.set_xlabel("Daily Return")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

def show_volatility_metrics(nav_data):
    returns = np.diff(nav_data)
    std_dev = np.std(returns)
    mean_return = np.mean(returns)
    risk_free_rate = 0.0001
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev if std_dev != 0 else 0

    peak = nav_data[0]
    max_drawdown = 0
    for nav in nav_data:
        if nav > peak:
            peak = nav
        drawdown = (peak - nav) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    st.markdown("### 📉 Volatility Metrics")
    st.markdown(f"- **Standard Deviation (NAV Return Volatility):** `{std_dev:.4f}`")
    st.markdown(f"- **Sharpe Ratio (Risk-adjusted Return):** `{sharpe_ratio:.4f}`")
    st.markdown(f"- **Maximum Drawdown:** `{max_drawdown * 100:.2f}%`")

def export_analysis_to_pdf(analysis, fund_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Gemini Analysis for {fund_name}\n\n{analysis}")
    output_path = f"{fund_name.replace(' ', '_')}_analysis.pdf"
    pdf.output(output_path)
    st.success(f"📄 PDF generated: {output_path}")
    with open(output_path, "rb") as f:
        st.download_button(label="📥 Download PDF", data=f, file_name=output_path, mime="application/pdf")

def show_badges(analysis, nav_data, articles, period):
    badges = []
    gain_percent = ((nav_data[-1] - nav_data[0]) / nav_data[0]) * 100
    if gain_percent > 10:
        badges.append(f"🏆 Top Gainer {period}")
    volatility = np.std(np.diff(nav_data))
    if volatility > 1.5:
        badges.append("🔻 High Risk")
    if len(articles) >= 3 or "buzz" in analysis.lower() or "trending" in analysis.lower():
        badges.append("🔥 Trending in News")
    if badges:
        st.markdown("### 🏅 Performance Badges")
        st.markdown(" ".join(badges))

if st.button("Analyze Fund Based on Latest News"):
    days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}
    days = days_map.get(timeframe, 30)

    for fund_name in selected_funds:
        st.header(f"📌 Analysis for: {fund_name}")
        with st.spinner("Fetching latest news and analyzing with Gemini..."):
            articles = fetch_news(fund_name)
            if not articles:
                st.warning("No relevant articles found. Showing general market insight.")
                prompt = f"You are a financial analyst. Provide a general market and sentiment analysis for mutual fund investors in the current global scenario."
            else:
                prompt = f"Based on the following news articles, analyze the sentiment, risk, and sectoral performance impacts for the mutual fund '{fund_name}':\n\n" + "\n\n".join(articles[:5])
            response = model.generate_content(prompt)
            analysis = response.text
            st.markdown("### 🔎 Gemini Insight")
            st.write(analysis)
            export_analysis_to_pdf(analysis, fund_name)

        nav_data = generate_dummy_nav(days)
        show_badges(analysis, nav_data, articles, timeframe)

        sentiment = "Neutral"
        color = "gray"
        if "positive" in analysis.lower(): sentiment, color = "Positive", "green"
        elif "negative" in analysis.lower(): sentiment, color = "Negative", "red"
        elif "bullish" in analysis.lower(): sentiment, color = "Bullish", "blue"
        elif "bearish" in analysis.lower(): sentiment, color = "Bearish", "orange"

        st.markdown("### 💬 Sentiment")
        st.markdown(f"<h3 style='color:{color}'>{sentiment}</h3>", unsafe_allow_html=True)

        matches = re.findall(r'([A-Za-z\s]+?)\s+(?:sector)?\s*(?:rose|gained|grew|dropped|declined|fell).*?(\d+)%?', analysis, re.IGNORECASE)
        if matches:
            sectors, impacts = zip(*matches)
            st.markdown("### 📌 Sector Impact")
            fig, ax = plt.subplots()
            ax.bar(sectors, list(map(int, impacts)), color='royalblue')
            ax.set_ylabel("Impact (%)")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.markdown("### 📊 NAV Performance")
        plot_nav_chart(nav_data, fund_name, timeframe)
        st.markdown("### 🔁 Return Distribution")
        plot_returns_histogram(nav_data)
        show_volatility_metrics(nav_data)
def plot_comparison_chart(nav_data_1, nav_data_2, fund_1, fund_2, period):
    if dark_mode: plt.style.use("dark_background")
    else: plt.style.use("default")
    
    days = len(nav_data_1)
    dates = [datetime.now() - timedelta(days=days - i) for i in range(days)]

    fig, ax = plt.subplots()
    ax.plot(dates, nav_data_1, label=fund_1, color='cyan')
    ax.plot(dates, nav_data_2, label=fund_2, color='magenta')
    ax.set_title(f"📊 NAV Comparison Over {period}")
    ax.set_xlabel("Date")
    ax.set_ylabel("NAV")
    ax.legend()
    fig.autofmt_xdate()
    st.pyplot(fig)

# If two funds are selected, show comparison chart
if fund_compare and len(selected_funds) == 2 and st.button("Compare Funds NAV Charts"):
    fund_1, fund_2 = selected_funds
    st.header(f"📊 NAV Comparison: {fund_1} vs {fund_2}")
    
    # Simulate NAVs again for fair comparison
    days = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}.get(timeframe, 30)
    nav_data_1 = generate_dummy_nav(days)
    nav_data_2 = generate_dummy_nav(days)
    
    plot_comparison_chart(nav_data_1, nav_data_2, fund_1, fund_2, timeframe)
