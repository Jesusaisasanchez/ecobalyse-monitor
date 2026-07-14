from playwright.sync_api import sync_playwright
import json
import smtplib
from email.mime.text import MIMEText
import os
import re

BRANDS = ["Adidas", "Nike", "Puma", "Decathlon", "Intersport France"]

DATA_FILE = "data.json"

EMAIL = "ecobalyse.monitor@gmail.com"
PASSWORD = "PASTE_YOUR_APP_PASSWORD_HERE"
TO = ["jesus.aisa@adidas.com"]

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for brand in BRANDS:
        try:
            page.goto(f"https://affichage-environnemental.ecobalyse.beta.gouv.fr/marques?search={brand}")
            page.wait_for_timeout(4000)

            text = page.inner_text("body")

            match = re.search(r"(\d+)\s+références produit", text)

            if match:
                results[brand] = int(match.group(1))
            else:
                results[brand] = None

        except:
            results[brand] = None

    browser.close()

# ✅ LOAD PREVIOUS
old = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        old = json.load(f)

# ✅ BUILD EMAIL
message = "Daily Ecobalyse Monitoring\n\n"

for brand in BRANDS:
    new = results.get(brand)
    prev = old.get(brand)

    if new is None:
        message += f"{brand}: no products yet\n"
    else:
        diff = new - (prev or 0)

        if diff > 0:
            message += f"✅ {brand}: {prev or 0} → {new} (+{diff})\n"
        else:
            message += f"{brand}: {prev or 0} → {new}\n"

# ✅ SAVE
with open(DATA_FILE, "w") as f:
    json.dump(results, f)

# ✅ SEND EMAIL
msg = MIMEText(message)
msg["Subject"] = "Ecobalyse Daily Tracking"
msg["From"] = EMAIL
msg["To"] = ", ".join(TO)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, TO, msg.as_string())

print("✅ Email sent")
