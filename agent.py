import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("PropGuard Radar Initializing...")

# Simple tracking setup
current_date = datetime.now().strftime("%Y-%m-%d")
alerts = []

# Target 1: PPRA Board
try:
    ppra_res = requests.get("https://theppra.org.za/", timeout=15)
    ppra_soup = BeautifulSoup(ppra_res.text, 'html.parser')
    for link in ppra_soup.find_all('a', limit=10):
        text = link.get_text().strip()
        if any(keyword in text.lower() for keyword in ["notice", "directive", "trust", "regulation"]):
            alerts.append({"source": "PPRA", "title": text, "date": current_date})
except Exception as e:
    print(f"PPRA check paused: {e}")

# Target 2: FIC Watchdog
try:
    fic_res = requests.get("https://www.fic.gov.za/", timeout=15)
    fic_soup = BeautifulSoup(fic_res.text, 'html.parser')
    for item in fic_soup.find_all(['a', 'h3'], limit=10):
        text = item.get_text().strip()
        if any(keyword in text.lower() for keyword in ["directive", "return", "compliance", "penalty"]):
            alerts.append({"source": "FIC", "title": text, "date": current_date})
except Exception as e:
    print(f"FIC check paused: {e}")

# Target 3: SACAA Drone Regulatory Watch
try:
    sacaa_res = requests.get("https://www.caa.co.za/Pages/RPAS/Remotely-Piloted-Aircraft-Systems.aspx", timeout=15)
    sacaa_soup = BeautifulSoup(sacaa_res.text, 'html.parser')
    for notice in sacaa_soup.find_all(['a', 'h4'], limit=15):
        title_text = notice.get_text().strip()
        if any(keyword in title_text.lower() for keyword in ["part 101", "notice", "directive"]):
            alerts.append({"source": "SACAA (Drone)", "title": title_text, "date": current_date})
except Exception as e:
    print(f"SACAA check paused: {e}")

# Display results in the log
if alerts:
    print(f"\n🚀 Found {len(alerts)} potential regulatory updates today:")
    for alert in alerts:
        print(f"[{alert['source']}] - {alert['title']}")
else:
    print("\n✅ Systems clear. No new critical compliance alerts detected today.")
