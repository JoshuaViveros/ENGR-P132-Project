from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time
import os


# -------------------------------
# CONFIG
# -------------------------------
SEARCH_QUERY = "laptops"
MIN_RATING = 3.5


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def extract_price(text):
    match = re.search(r'Now\s*\$([\d,]+\.\d{2})', text)
    if not match:
        match = re.search(r'([\d,]+\.\d{2})', text)
    return float(match.group(1).replace(",", "")) if match else None


def extract_rating(item):
    rating_container = item.find_elements(By.CSS_SELECTOR, '[data-testid="product-ratings"]')
    if not rating_container:
        return 0

    stars = rating_container[0].find_elements(By.CSS_SELECTOR, 'svg')
    rating = 0

    for star in stars:
        cls = star.get_attribute("class")
        if "halfFilled" in cls:
            rating += 0.5
        elif "filled" in cls:
            rating += 1

    return rating


def calculate_score(price, rating):
    return ((rating ** 3) * (1 + (rating - 4))) / ((price ** 0.65) + 1)


def get_verdict(score):
    if score > 5:
        return "🔥 Excellent value"
    elif score > 4:
        return "💰 Budget winner"
    elif score > 3:
        return "⚖️ Balanced pick"
    else:
        return "👍 Decent option"


def shorten(text, max_len=65):
    return text[:max_len] + "..." if len(text) > max_len else text


# -------------------------------
# MAIN SCRIPT
# -------------------------------

driver = Driver(
    browser="firefox",
    user_data_dir="/home/joshua/.config/mozilla/firefox/apdj47z9.Test",
    headless=False
)

try:
    url = f"https://www.walmart.com/search?q={SEARCH_QUERY}"
    driver.get(url)

    # wait for items
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-item-id]'))
    )

    # let page fully settle
    time.sleep(5)

    # light scroll (not aggressive)
    driver.execute_script("window.scrollBy(0, 800)")
    time.sleep(2)

    items = driver.find_elements(By.CSS_SELECTOR, '[data-item-id]')

    results = []
    seen_titles = set()

    for item in items:
        try:
            # --- TITLE ---
            title_el = item.find_element(By.CSS_SELECTOR, 'h3[data-automation-id="product-title"]')
            title = title_el.text.strip()

            if not title or title in seen_titles:
                continue

            # --- PRICE ---
            price_el = item.find_element(By.CSS_SELECTOR, '[data-automation-id="product-price"]')
            price = extract_price(price_el.text.strip())

            if price is None:
                continue

            # --- RATING ---
            rating = extract_rating(item)

            if rating < MIN_RATING:
                continue

            # --- SCORE ---
            score = calculate_score(price, rating)

            results.append((title, price, rating, score))
            seen_titles.add(title)

        except:
            continue

    # -------------------------------
    # SORT RESULTS
    # -------------------------------
    results.sort(key=lambda x: x[3], reverse=True)

    # -------------------------------
    # OUTPUT
    # -------------------------------
    os.system("clear")  # use "cls" on Windows

    print("=" * 80)
    print("🛒 Walmart Laptop Deal Finder")
    print(f"🔍 Search: \"{SEARCH_QUERY}\"")
    print("📊 Ranked by: Custom Value Score")
    print("=" * 80)

    print("\n🏆 TOP 10 BEST VALUE PICKS\n")

    medals = ["🥇", "🥈", "🥉"]

    for i, (title, price, rating, score) in enumerate(results[:10]):
        medal = medals[i] if i < 3 else "  "

        print(f"{i+1:>2}. {medal} {shorten(title)}")
        print(f"    💰 Price   : ${price:,.2f}")
        print(f"    ⭐ Rating  : {rating:.1f} / 5")
        print(f"    📊 Score   : {score:.4f}")
        print(f"    🧠 Verdict : {get_verdict(score)}")
        print("-" * 80)

    if not results:
        print("⚠️ No results found (possible soft block)")

finally:
    input("\nPress ENTER to close browser...")
    driver.quit()
    