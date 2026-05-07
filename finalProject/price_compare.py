from seleniumbase import SB, Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


MAX_RESULTS = 5
SEARCH_QUERY = input("Enter product to search: ")


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def price_to_float(price_text):
    if not price_text:
        return None

    match = re.search(r"\$?([\d,]+\.?\d*)", price_text)

    if match:
        return float(match.group(1).replace(",", ""))

    return None


# -------------------------------
# AMAZON SCRAPER
# -------------------------------

def scrape_amazon_product(sb, url):
    sb.open(url)
    sb.wait_for_element("#productTitle", timeout=10)

    title = sb.get_text("#productTitle").strip()
    price = "Price not found"

    price_selectors = [
        "#corePriceDisplay_desktop_feature_div span.a-offscreen",
        "span.a-price span.a-offscreen",
        ".a-price .a-offscreen"
    ]

    for selector in price_selectors:
        if sb.is_element_present(selector):
            temp_price = sb.get_text(selector)

            if "$" in temp_price:
                price = temp_price
                break

    rating = "Rating not found"

    if sb.is_element_present("span.a-icon-alt"):
        rating = sb.get_text("span.a-icon-alt")

    return {
        "website": "Amazon",
        "title": title,
        "price": price,
        "price_number": price_to_float(price),
        "rating": rating,
        "url": url
    }


def get_amazon_results(search_query):
    products = []

    with SB(uc=True, headless=False) as sb:
        sb.open("https://www.amazon.com")

        sb.type("#twotabsearchtextbox", search_query)
        sb.click("#nav-search-submit-button")

        sb.wait_for_element("div.s-main-slot", timeout=10)

        links = sb.find_elements("a.a-link-normal.s-no-outline")

        urls = []

        for link in links:
            href = link.get_attribute("href")

            if href and "/dp/" in href and href not in urls:
                urls.append(href)

            if len(urls) == MAX_RESULTS:
                break

        for i, url in enumerate(urls, start=1):
            try:
                print(f"Scraping Amazon product {i}...")
                product = scrape_amazon_product(sb, url)

                if product["price_number"] is not None:
                    products.append(product)

            except Exception as e:
                print(f"Amazon product {i} skipped: {e}")

    return products


# -------------------------------
# WALMART SCRAPER
# -------------------------------

def extract_walmart_rating(item):
    rating_container = item.find_elements(By.CSS_SELECTOR, '[data-testid="product-ratings"]')

    if not rating_container:
        return 0

    stars = rating_container[0].find_elements(By.CSS_SELECTOR, "svg")
    rating = 0

    for star in stars:
        cls = star.get_attribute("class")

        if "halfFilled" in cls:
            rating += 0.5
        elif "filled" in cls:
            rating += 1

    return rating


def get_walmart_results(search_query):
    products = []

    driver = Driver(
        browser="chrome",
        headless=False
    )

    try:
        url = f"https://www.walmart.com/search?q={search_query}"
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-item-id]"))
        )

        time.sleep(5)
        driver.execute_script("window.scrollBy(0, 800)")
        time.sleep(2)

        items = driver.find_elements(By.CSS_SELECTOR, "[data-item-id]")

        seen_titles = set()

        for item in items:
            try:
                title_el = item.find_element(
                    By.CSS_SELECTOR,
                    'h3[data-automation-id="product-title"]'
                )

                title = title_el.text.strip()

                if not title or title in seen_titles:
                    continue

                price_el = item.find_element(
                    By.CSS_SELECTOR,
                    '[data-automation-id="product-price"]'
                )

                price_text = price_el.text.strip()
                price_number = price_to_float(price_text)

                if price_number is None:
                    continue

                rating = extract_walmart_rating(item)

                link_el = item.find_element(By.CSS_SELECTOR, "a")
                product_url = link_el.get_attribute("href")

                if product_url and product_url.startswith("/"):
                    product_url = "https://www.walmart.com" + product_url

                products.append({
                    "website": "Walmart",
                    "title": title,
                    "price": f"${price_number:,.2f}",
                    "price_number": price_number,
                    "rating": rating,
                    "url": product_url
                })

                seen_titles.add(title)

                if len(products) == MAX_RESULTS:
                    break

            except Exception:
                continue

    finally:
        driver.quit()

    return products


# -------------------------------
# MAIN PROGRAM
# -------------------------------

if __name__ == "__main__":
    walmart_products = get_walmart_results(SEARCH_QUERY)
    amazon_products = get_amazon_results(SEARCH_QUERY)

    all_products = amazon_products + walmart_products

    valid_products = [
        product for product in all_products
        if product["price_number"] is not None
    ]

    print("\n==============================")
    print(" ALL RESULTS ")
    print("==============================")

    for i, product in enumerate(valid_products, start=1):
        print(f"\nProduct {i}")
        print(f"Website: {product['website']}")
        print(f"Title: {product['title']}")
        print(f"Price: {product['price']}")
        print(f"Rating: {product['rating']}")
        print(f"URL: {product['url']}")

    print("\n==============================")
    print(" LOWEST PRICE OVERALL ")
    print("==============================")

    if valid_products:
        lowest = min(valid_products, key=lambda x: x["price_number"])

        print(f"Website: {lowest['website']}")
        print(f"Title: {lowest['title']}")
        print(f"Price: {lowest['price']}")
        print(f"Rating: {lowest['rating']}")
        print(f"URL: {lowest['url']}")

    else:
        print("No valid prices were found.")