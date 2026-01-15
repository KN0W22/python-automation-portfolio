import json
import time
import os
import random
from playwright.sync_api import sync_playwright

base_path = os.path.dirname(os.path.abspath(__file__))

output_folder = os.path.join(base_path, "Data to Scrape")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

data_collected = []

def handle_response(response):
    try:
        if "search_items" in response.url and response.status == 200:
            print(f"  [Background] Detected Search API: {response.url[:60]}...")
            
            json_data = response.json()
            if 'items' in json_data:
                items = json_data['items']
                data_collected.extend(items)
                print(f"  [Background] + Added {len(items)} items to list. (Total: {len(data_collected)})")
            else:
                print("  [Background] JSON found but no 'items' key.")
    except Exception:
        pass

def run():
    search_query = input("What product would you like to search for? ")
    try:
        pages_to_scrape = int(input("How many pages would you like to scrape? "))
    except ValueError:
        pages_to_scrape = 1

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./my_shopee_profile", 
            headless=False,
            viewport={"width": 1280, "height": 720},
            args=['--disable-blink-features=AutomationControlled', '--start-maximized'],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )   
        page = context.pages[0]

        page.on("response", handle_response)
        
        print("--- Opening Shopee... ---")
        page.goto("https://shopee.ph")
        
        print("\n" + "="*50)
        print("CHECKPOINT: Please Log In if needed.")
        input("Press ENTER once you are logged in and on the homepage...\n")

        print(f"--- Searching for: {search_query} ---")
        try:
            search_input = page.wait_for_selector('input.shopee-searchbar-input__input', timeout=5000)
            if search_input:
                search_input.click()
                page.keyboard.type(search_query, delay=100) 
                time.sleep(0.5)
                page.keyboard.press("Enter")
            else:
                print("Search bar not found, forcing navigation...")
                page.goto(f"https://shopee.ph/search?keyword={search_query.replace(' ', '%20')}")

        except Exception as e:
            print(f"Search interaction failed: {e}")
            page.goto(f"https://shopee.ph/search?keyword={search_query.replace(' ', '%20')}")

        time.sleep(5)

        for page_number in range(pages_to_scrape):
            if page_number > 0:
                print(f"Navigating to Page {page_number + 1}...")
                encoded_query = search_query.replace(" ", "%20")
                page.goto(f"https://shopee.ph/search?keyword={encoded_query}&page={page_number}")

                time.sleep(random.uniform(5, 8))

            if "verify" in page.title().lower() or "login" in page.title().lower():
                print("!!! CAPTCHA DETECTED !!!")
                input("Solve it in browser, then press ENTER to continue...")

        context.close()

    filename = f"{search_query.replace(' ', '_')}_results.json"
    full_save_path = os.path.join(output_folder, filename) 

    with open(full_save_path, 'w', encoding='utf-8') as f:
        json.dump(data_collected, f, indent=2)

    print(f"\n--- Done! Saved {len(data_collected)} items to: ---")
    print(f"{full_save_path}")

if __name__ == "__main__":
    run()