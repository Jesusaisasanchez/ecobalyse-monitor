import requests
import json
import smtplib
from email.mime.text import MIMEText
import os

# ✅ CONFIG
BRANDS = ["Adidas", "Nike", "Puma", "Decathlon", "Intersport France"]

DATA_FILE = "data.json"

EMAIL = "ecobalyse.monitor@gmail.com"
PASSWORD = "PASTE_YOUR_APP_PASSWORD_HERE"
TO = ["jesus.aisa@adidas.com"]

results = {}

# ✅ REAL API (this works)
API_URL = "https://affichage-environnemental.ecobalyse.beta.gouv.fr/api/marques"

try:
    response = requests.get(API_URL)
    data = response.json()

    for brand in BRANDS:
        found = False

        for item in data:
            name = item.get("nom", "").lower()

            if brand.lower() in name:
                results[brand] = item.get("nbReferences", 0)
                found = True
                break

        if not found:
            results[brand] = None

except:
    for brand in BRANDS:
        results[brand] = None


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
