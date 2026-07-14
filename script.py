import requests
import re
import json
import smtplib
from email.mime.text import MIMEText
import os
from bs4 import BeautifulSoup

# ✅ CONFIG
BRANDS = ["Adidas", "Nike", "Puma", "Decathlon", "Intersport France"]

DATA_FILE = "data.json"

EMAIL = "ecobalyse.monitor@gmail.com"
PASSWORD = "sbgo mqwx pnyq qhat"
TO = ["jesus.aisa@adidas.com"]

results = {}

# ✅ FETCH DATA (correct logic: search → open brand page → extract count)
for brand in BRANDS:
    try:
        search_url = f"https://affichage-environnemental.ecobalyse.beta.gouv.fr/marques?search={brand}"

        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # find first valid brand link
        link = soup.find("a", href=True)

        if link and "/marques/" in link["href"]:
            brand_url = "https://affichage-environnemental.ecobalyse.beta.gouv.fr" + link["href"]

            response2 = requests.get(brand_url)
            text = response2.text

            match = re.search(r"(\d+)\s+références produit", text)

            if match:
                results[brand] = int(match.group(1))
            else:
                results[brand] = None
        else:
            results[brand] = None

    except:
        results[brand] = None


# ✅ LOAD PREVIOUS DATA
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

# ✅ SAVE DATA
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
