import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# ✅ Configure Gemini with your API key (v1 will be used automatically)
genai.configure(api_key="Replace with your key")  # Replace with your key

# ✅ Load the Gemini model (correct syntax for v1)
model = genai.GenerativeModel("gemini-pro")

# Function to fetch dummy mutual fund data
def get_mutual_fund_data(fund_name):
    return {
        "Fund Name": fund_name,
        "NAV": "₹72.55",
        "1 Year Return": "+12.35%",
        "AUM": "₹15,000 Cr",
        "Category": "Large Cap"
    }

# Scrape news using Google Search
def get_news_about_fund(fund_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f"{fund_name} mutual fund news"
    url = f"https://www.google.com/search?q={query}&tbm=nws"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    news_list = []
    for item in soup.select("div.dbsr")[:5]:
        title = item.select_one("div.JheGif.nDgy9d").text
        link = item.a['href']
        snippet = item.select_one("div.Y3v8qd").text
        news_list.append({"title": title, "link": link, "snippet": snippet})
    return news_list

# Gemini prompt function
def generate_insight(fund_data, news_list):
    news_summary = "\n".join([f"- {n['title']}: {n['snippet']}" for n in news_list])
    prompt = f"""
    Here's data for a mutual fund:
    {fund_data}

    Recent news headlines and summaries:
    {news_summary}

    Give a short analysis on the fund’s recent performance and future outlook.
    """
    response = model.generate_content(prompt)
    return response.text

# Streamlit UI
st.title("📈 Mutual Fund Analyzer (Powered by Gemini AI)")
fund_name = st.text_input("Enter Mutual Fund Name")

if st.button("Analyze"):
    if not fund_name.strip():
        st.warning("Please enter a mutual fund name.")
    else:
        st.info("Fetching data and generating insight...")
        fund_data = get_mutual_fund_data(fund_name)
        news_list = get_news_about_fund(fund_name)
        explanation = generate_insight(fund_data, news_list)

        st.subheader("📊 Fund Overview")
        for k, v in fund_data.items():
            st.write(f"**{k}:** {v}")

        st.subheader("📰 Latest News")
        for news in news_list:
            st.markdown(f"- [{news['title']}]({news['link']}) — {news['snippet']}")

        st.subheader("🤖 Gemini's Insight")
        st.write(explanation)
