import os
import requests
from playwright.sync_api import sync_playwright
import pandas as pd
from urllib.parse import urljoin
import time

base_path = r"C:\Users\junma\Python Code\Python-Automation-Portfolio\E-Commerce Asset Migration Bot"
output_folder = os.path.join(base_path, "Cheap_Pokemon_Images")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def run():
    with sync_playwright() as p:
        
        print("Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("Going to website...")
        page.goto("https://scrapeme.live/shop/")

        all_data = []

        while True:
            try:
                page.wait_for_selector("li.product", timeout=5000)
            except:
                print("Timed out waiting for products (or reached end).")
                break

            all_products = page.locator("li.product")
            total = all_products.count()
            
            print(f"Checking {total} products on this page...")

            for i in range(total):
                current_product = all_products.nth(i)

                price_element = current_product.locator("span.woocommerce-Price-amount").last
                
                if not price_element.is_visible():
                    continue
                    
                price = price_element.inner_text()
                clean_price_text = price.replace("£", "").strip().replace(",", "")

                try:
                    price_value = float(clean_price_text)
                except ValueError:
                    continue

                if price_value <= 50:
                    title = current_product.locator("h2").inner_text()
                    safe_filename = title.replace(":", "-").replace("/", "-").replace('"', '').replace("'", "") + ".jpg"

                    image = current_product.locator("img").first.get_attribute("src")
                    full_image_url = urljoin(page.url, image)

                    print(f"✅ Found Cheap Item: {title} (£{price_value:.2f}) - Downloading...")

                    try:
                        img_data = requests.get(full_image_url).content
                        save_path = os.path.join(output_folder, safe_filename)
                        
                        with open(save_path, "wb") as handler:
                            handler.write(img_data)
                    except Exception as e:
                        print(f"❌ Failed to download {title}: {e}")

                    all_data.append({
                        "Title": title,
                        "Price": price_value,
                        "Image File": safe_filename
                    })

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            next_button = page.locator("a.next.page-numbers").first

            if next_button.is_visible():
                print("Navigating to next page...")
                next_button.click()
                time.sleep(2) 
            else:
                print("No more pages to navigate.")
                break

        print("Run complete.")

        if all_data:
            df = pd.DataFrame(all_data)
            csv_path = os.path.join(base_path, "cheap_pokemon_data.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved data to {csv_path}")
            
        browser.close()

if __name__ == "__main__":
    run()