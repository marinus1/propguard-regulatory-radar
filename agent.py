import os
import requests
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
import gspread
import google.generativeai as genai
from datetime import datetime

# 1. Setup API Keys & Secret Variables
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GOOGLE_CREDS_JSON = os.environ["GOOGLE_CREDS_JSON"]

genai.configure(api_key=GEMINI_API_KEY)

# 2. Connect to the Free Google Sheet
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(eval(GOOGLE_CREDS_JSON), scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("propguard-regulatory-radar").sheet1

# 3. Scrape the Real-Estate Statutory Boards (PPRA & FIC)
def scrape_boards():
    alerts = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Target A: PPRA News Portal
    try:
        ppra_res = requests.get("https://theppra.org.za/news/", timeout=15)
        ppra_soup = BeautifulSoup(ppra_res.text, 'html.parser')
        # Grabbing titles from the main news loops
        for headline in ppra_soup.find_all(['h2', 'h3', 'a'], limit=15):
            title_text = headline.get_text().strip()
            if "Notice" in title_text or "PDE" in title_text or "CPD" in title_text or "Trust" in title_text or "FFC" in title_text:
                alerts.append({"source": "PPRA Board", "title": title_text, "date": current_date})
    except Exception as e:
        print(f"PPRA Scrape temporary bypass: {e}")

    # Target B: FIC Newsroom Portal
    try:
        fic_res = requests.get("https://www.fic.gov.za/newsroom/", timeout=15)
        fic_soup = BeautifulSoup(fic_res.text, 'html.parser')
        for row in fic_soup.find_all(['a', 'td'], limit=20):
            title_text = row.get_text().strip()
            if "Directive" in title_text or "Notice" in title_text or "Compliance" in title_text or "RCR" in title_text:
                alerts.append({"source": "FIC Watchdog", "title": title_text, "date": current_date})
    except Exception as e:
        print(f"FIC Scrape temporary bypass: {e}")
        
    return alerts

# 4. Use Gemini 2.5 Flash to Generate a Gap-Analysis Report
def analyze_with_gemini(source, headline):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an elite South African Real Estate Compliance Officer working for an internal protection agency loop.
    
    Analyze this headline caught on a live scan:
    Source: {source}
    Headline: {headline}
    
    Translate this regulatory update into plain, high-stakes operational commands for an Estate Agency Principal Agent.
    Your response must be brief and structured as exactly 3 short, bold action items using numbers (1️⃣, 2️⃣, 3️⃣) explaining what they need to fix, check, or audit immediately to protect their license to trade (FFC) or avoid massive audit penalties. Include an estimated timeline or deadline if implied.
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

# 5. Run the Autonomous Automation Loop
def run_agent():
    print("Scout Agent waking up...")
    scraped_alerts = scrape_boards()
    
    # Get existing logs in the sheet to prevent duplicates
    existing_headlines = sheet.col_values(3)
    
    # If the sheet is brand new, let's make sure it doesn't break
    if not existing_headlines:
        existing_headlines = []

    for alert in scraped_alerts:
        if alert["title"] not in existing_headlines:
            print(f"🚨 New Compliance Target Detected: {alert['title']}")
            
            # Run the Brain
            ai_analysis = analyze_with_gemini(alert["source"], alert["title"])
            
            # Post directly to the Master Command Center Google Sheet
            sheet.append_row([alert["date"], alert["source"], alert["title"], ai_analysis])
            print("Successfully logged to Dashboard.")
        else:
            print(f"Bypassing duplicate: {alert['title']}")

if __name__ == "__main__":
    run_agent()
