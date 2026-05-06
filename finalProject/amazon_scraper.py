from seleniumbase import SB
import re


MAX_RESULTS = 10


def price_to_float(price_text):
    if not price_text:
        return None

    match = re.search(r"\$([\d,]+\.?\d*)", price_text)

    if match:
        return float(match.group(1).replace(",", ""))

    return None


def scrape_product(sb, url):
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
        "title": title,
        "price": price,
        "price_number": price_to_float(price),
        "rating": rating,
        "url": url
    }


def get_g502_data():
    with SB(uc=True, headless=False) as sb:

        sb.open("https://www.amazon.com")

        sb.type("#twotabsearchtextbox", "Logitech G502 gaming mouse")

        sb.click("#nav-search-submit-button")

        sb.wait_for_element("div.s-main-slot", timeout=10)

        # Get all search result links
        links = sb.find_elements("a.a-link-normal.s-no-outline")

        urls = []

        for link in links:

            href = link.get_attribute("href")

            # Only keep real Amazon product links
            if href and "/dp/" in href and href not in urls:
                urls.append(href)

            # Stop after MAX_RESULTS
            if len(urls) == MAX_RESULTS:
                break

        print(f"\nCollected {len(urls)} product URLs")

        products = []

        # Scrape each product page
        for i, url in enumerate(urls, start=1):

            print(f"\nScraping product {i}...")

            try:
                product = scrape_product(sb, url)

                products.append(product)

                print(f"Found: {product['title']}")
                print(f"Price: {product['price']}")

            except Exception as e:
                print(f"Error scraping product {i}: {e}")

        # Keep only products with valid prices
        valid_products = [
            product for product in products
            if product["price_number"] is not None
        ]

        lowest = None

        if valid_products:
            lowest = min(valid_products, key=lambda x: x["price_number"])

        return {
            "products": products,
            "lowest": lowest
        }


if __name__ == "__main__":

    data = get_g502_data()

    print("\n==============================")
    print(" AMAZON SCRAPER RESULTS ")
    print("==============================")

    for i, product in enumerate(data["products"], start=1):

        print(f"\nProduct {i}")
        print(f"Title: {product['title']}")
        print(f"Price: {product['price']}")
        print(f"Rating: {product['rating']}")
        print(f"URL: {product['url']}")

    print("\n==============================")
    print(" LOWEST PRICE FOUND ")
    print("==============================")

    if data["lowest"]:

        print(f"Title: {data['lowest']['title']}")
        print(f"Price: {data['lowest']['price']}")
        print(f"Rating: {data['lowest']['rating']}")
        print(f"URL: {data['lowest']['url']}")

    else:
        print("No valid prices were found.")