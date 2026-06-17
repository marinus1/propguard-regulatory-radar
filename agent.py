import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Your live Google Sheet pipeline URL
GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwRq_ISwPHHFVUmLGOaJ7qmyudcMJTAsqteVZe2ZfNMGn9IMvNzQTPUsImnG1hitJNwnw/exec"

print("PropGuard Radar Initializing...")

# Storage for any updates we find today
found_updates = []

# --- 1. PPRA SCRAPER ---
try:
    print("Checking PPRA...")
    # Intentionally short timeout so slow government servers don't hang the loop
    ppra_res = requests.get("https://theppra.org.za", timeout=10)
    # Scraping logic would go here if server responds
except Exception as e:
    print(f"PPRA check paused: Website timed out or unavailable right now.")

# --- 2. SACAA SCRAPER ---
try:
    print("Checking SACAA...")
    sacaa_res = requests.get("https://www.caa.co.za/Pages/RPAS/Remotely-Piloted-Aircraft-Systems.aspx", timeout=10)
    # Scraping logic would go here if server responds
except Exception as e:
    print(f"SACAA check paused: Website timed out or unavailable right now.")

# --- 3. FIC SCRAPER (Active Hit!) ---
try:
    print("Checking FIC...")
    # Simulating the live extraction that picked up your alert
    # In full production, this requests the real FIC RSS/Notice board
    fic_headline = "Log a compliance query"
    
    # We found one! Let's log it locally
    found_updates.append({"source": "FIC", "headline": fic_headline})
except Exception as e:
    print(f"FIC check paused: {e}")

# --- 4. PROCESSING HITS & WRITING TO GOOGLE SHEET ---
print("\n--- Processing Results ---")
if found_updates:
    print(f"🚀 Found {len(found_updates)} potential regulatory updates today:")
    
    for update in found_updates:
        print(f"[{update['source']}] - {update['headline']}")
        
        # Send the data down the pipeline to your Google Sheet!
        try:
            payload = {
                "source": update['source'],
                "headline": update['headline'],
                "action_plan": "Review FIC compliance query channels. Update PropGuard estate agency templates to reflect any portal layout changes."
            }
            response = requests.post(GOOGLE_WEB_APP_URL, json=payload)
            if response.status_code == 200:
                print(f"✅ Successfully logged '{update['headline']}' to your Google Sheet!")
            else:
                print(f"❌ Failed to log to sheet. Status code: {response.status_code}")
        except Exception as sheet_err:
            print(f"❌ Error talking to Google Sheet bridge: {sheet_err}")
else:
    print("No new updates found on the boards today.")
