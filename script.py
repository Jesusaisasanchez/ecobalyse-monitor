import requests
import json
import smtplib
from email.mime.text import MIMEText
import os
import re

# ✅ CONFIG
BRANDS = ["Adidas", "Nike", "Puma", "Decathlon", "Intersport France"]

BASE_URL = "https://affichage-environnemental.ecobalyse.beta.gouv.fr/api/marques?search="

DATA_FILE = "data.json"

EMAIL = "ecobalyse.monitor@gmail.com"
PASSWORD = "sbgo mqwx pnyq qhat"
TO = "jesus.aisa@adidas.com"

results = {}

# ✅ FETCH DATA
for brand in BRANDS:
    try:
        search_url = f"https://affichage-environnemental.ecobalyse.beta.gouv.fr/marques?search={brand}"

        response = requests.get(search_url)
        text = response.text

        match = re.search(r"(\d+)\s+références produit", text)

        if match:
            results[brand] = int(match.group(1))
           
        else:
            results[brand] = None
            
        except:
            results[brand] = None


# ✅ LOAD PREVIOUS
old = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        old = json.load(f)

# ✅ BUILD EMAIL
message = "Daily Ecobalyse Monitoring\n\n"

for brand in BRANDS:
    try:
        search_url = f"https://affichage-environnemental.ecobalyse.beta.gouv.fr/marques?search={brand}"

        response = requests.get(search_url)
        text = response.text

        match = re.search(r"(\d+)\s+références produit", text)

        if match:
            results[brand] = int(match.group(1))
        else:
            results[brand] = None

    except:
        results[brand] = None

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
