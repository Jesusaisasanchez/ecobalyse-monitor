from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import json
import smtplib
from email.mime.text import MIMEText
import os
import re

# ✅ CONFIG (Adidas first)
BRANDS = ["Adidas", "Nike", "Puma", "Decathlon", "Intersport France"]
URL = "https://affichage-environnemental.ecobalyse.beta.gouv.fr/"
DATA_FILE = "data.json"

EMAIL = "ecobalyse.monitor@gmail.com"
PASSWORD = "sbgo mqwx pnyq qhat"
TO = "jesus.aisa@adidas.com", "Maira.SchillerBecerra@adidas.com"

# ✅ HEADLESS BROWSER (GitHub compatible)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


driver.get(URL)
time.sleep(5)

results = {}

for brand in BRANDS:
    try:
        search = driver.find_element(By.TAG_NAME, "input")
        search.clear()
        search.send_keys(brand)
        search.send_keys(Keys.RETURN)
        time.sleep(5)

        page_text = driver.find_element(By.TAG_NAME, "body").text

        match = re.search(r"(\d+)\s+références produit", page_text)

        if match:
            results[brand] = int(match.group(1))
        else:
            results[brand] = None

        driver.get(URL)
        time.sleep(3)

    except:
        results[brand] = None

driver.quit()

# ✅ Load previous
old = {}
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        old = json.load(f)

# ✅ Build email
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

# ✅ Save new
with open(DATA_FILE, "w") as f:
    json.dump(results, f)

# ✅ Send email
msg = MIMEText(message)
msg["Subject"] = "Ecobalyse Daily Tracking"
msg["From"] = EMAIL
msg["To"] = ", ".join(TO)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, TO, msg.as_string())
