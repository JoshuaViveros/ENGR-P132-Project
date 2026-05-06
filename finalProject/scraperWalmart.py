from seleniumbase import Driver
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math
import time, random




# Start Firefox browser
driver = Driver(
    browser="firefox",
    user_data_dir="/home/joshua/.config/mozilla/firefox/apdj47z9.Test",
    headless=False
)
try:
    driver.get("https://www.walmart.com/search?q=laptops")

    WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-item-id]'))
)
    time.sleep(random.uniform(3, 6))
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def is_blocked(driver):
        page = driver.page_source.lower()
        return "robot" in page or "verify" in page or "captcha" in page

    def load_page(driver):
        driver.get("https://www.walmart.com/search?q=laptops")
        time.sleep(5)

        page = driver.page_source.lower()
        if "robot" in page or "captcha" in page:
            return False
        return True

    for attempt in range(3):
        if load_page(driver):
            break
        print("Blocked, retrying...")
        time.sleep(random.uniform(10, 20))
    else:
        print("Failed after retries")
        driver.quit()
        exit()

    driver.get("https://www.walmart.com/search?q=laptops")

    time.sleep(5)

    if is_blocked(driver):
        print("Blocked. Retrying...")
        driver.quit()
        time.sleep(random.uniform(10, 20))
        driver.get("https://www.walmart.com/search?q=laptops")

    for _ in range(random.randint(3, 7)):
        driver.execute_script("window.scrollBy(0, arguments[0])", random.randint(200, 900))
        time.sleep(random.uniform(1.0, 3.0))

    time.sleep(random.uniform(4, 8))

    items = driver.find_elements(By.CSS_SELECTOR, '[data-item-id]')
    seen = set()
    results = []

    for item in items:
        try:

            

        # Get title
            title_el = item.find_element(By.CSS_SELECTOR, 'h3[data-automation-id="product-title"]')
            title = title_el.text.strip()

            # Get price text
            price_el = item.find_element(By.CSS_SELECTOR, '[data-automation-id="product-price"]')
            text = price_el.text.strip()

            # Extract price
            match = re.search(r'Now\s*\$([\d,]+\.\d{2})', text)
            if not match:
                match = re.search(r'([\d,]+\.\d{2})', text)

            if not match:
                continue
            
            price = match.group(1)
            price_float = float(price.replace(",", ""))


            ### Rating 
            rating_container = item.find_elements(By.CSS_SELECTOR, '[data-testid="product-ratings"]')
            rating = 0
            if rating_container:
                stars = rating_container[0].find_elements(By.CSS_SELECTOR, 'svg')

         
                for star in stars:
                    cls = star.get_attribute("class")

                    ### Rating 
                    if "halfFilled" in cls:
                        rating += 0.5
                    elif "filled" in cls:
                        rating += 1

            else:
                rating = 0
            rating_float = rating
            # Star filter
            if rating_float < 3.5:
                continue
        
            score = (
                (rating_float ** 3) * (1 + (rating_float - 4))
            ) / (
                (price_float ** 0.65) + 1
            )

            results.append((title, price_float, rating_float, score))

        except:
            continue

    results.sort(key=lambda x: x[3], reverse=True)

    for item in results[:10]:
        print(f"{item[0]} - ${item[1]} - {item[2]}⭐ - score: {item[3]:.4f}")

            # for item in items:
            #     try:
            #         title_el = item.find_element(By.CSS_SELECTOR, 'h3[data-automation-id="product-title"]')
            #         price_el = item.find_element(By.CSS_SELECTOR, '[data-automation-id="product-price"]')

            #         print("FOUND ITEM")  # debug

            #     except Exception as e:
            #         print("SKIPPED:", e)
        
        
    

finally:
    driver.quit()



