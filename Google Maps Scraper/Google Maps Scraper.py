from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import re

base_path = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(base_path, "Leads")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

Data_Scraped = []

def scrape_google_maps():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--lang=en-US"])
        page = browser.new_page()

        print("📍 navigating to Google Maps...")
        page.goto("https://www.google.com/maps", timeout=60000)

        try:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2) 

            search_box = page.get_by_role("textbox").first
            if not search_box.is_visible():
                search_box = page.locator("input").first
            
            search_box.click()

            search = input("Enter a search term: ")
            try:
                target_count = int(input("How many leads do you want? (e.g. 10): "))
            except ValueError:
                print("Invalid number. Defaulting to 10.")
                target_count = 10
            print(f"🔍 Searching for: {search}")
            search_box.fill(search)
            page.keyboard.press("Enter")
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return
        
        print("🔍 Searching...")
        try:
            page.wait_for_selector('div[role="feed"]', timeout=15000)
        except:
            print("⚠️ Could not find the results list. Google might have blocked the view.")
            return

        print(f"📜 Scrolling until we find at least {target_count} businesses...")
        place_urls = []
        no_new_data_counter = 0
        
        while len(set(place_urls)) < target_count:
            page.hover('div[role="feed"]')
            page.mouse.wheel(0, 5000)
            time.sleep(1.5)
            
            all_links = page.locator("a").all()
            current_count = len(place_urls)
            
            for link in all_links:
                href = link.get_attribute("href")
                if href and ("/maps/place/" in href or "google.com/maps" in href):
                    place_urls.append(href)

            unique_count = len(set(place_urls))
            print(f"   -> Found {unique_count} unique links so far...")
            if len(place_urls) == current_count:
                no_new_data_counter += 1
                if no_new_data_counter > 3:
                    print("⚠️ No new results found after scrolling. Stopping scroll.")
                    break
            else:
                no_new_data_counter = 0

            if len(place_urls) > 500: 
                break

        unique_urls = list(set(place_urls))
        print(f"🎉 Stopped scrolling. Found {len(unique_urls)} total businesses.")
        
        for index, url in enumerate(unique_urls):
            if index >= target_count: 
                print(f"🛑 Reached target of {target_count} leads. Stopping.")
                break

            print(f"[{index+1}/{min(len(unique_urls), target_count)}] Visiting result...")
            time.sleep(2)
            try:
                page.goto(url, timeout=30000)
                page.wait_for_selector("h1", timeout=5000)

                rating = "N/A"
                main_div = page.locator('div[role="main"]')
                star_el = main_div.get_by_label(re.compile(r"^\d\.\d stars")).first

                if star_el.count() > 0:
                    aria_label = star_el.get_attribute("aria-label")
                    rating = aria_label.split(" ")[0]

                name = page.locator("h1").inner_text()
                website_locator = page.locator('a[data-item-id="authority"]')
                website = website_locator.get_attribute("href") if website_locator.count() > 0 else "No Website"
                phone_locator = page.locator('button[data-item-id^="phone:"]')
                if phone_locator.count() > 0:
                    phone = phone_locator.get_attribute("aria-label").replace("Phone: ", "")
                else:
                    phone = "No Phone"

                Data_Scraped.append({
                    "Name": name,
                    "Rating": rating,
                    "Website": website,
                    "Phone": phone
                })
            except Exception as e:
                print(f"   ❌ Error scraping this item: {e}")
                continue

        print("🎉 Scraping Complete!")
        browser.close()

        if Data_Scraped:
            df = pd.DataFrame(Data_Scraped)
            safe_name = search.replace(" ", "_")
            filename = f"{output_folder}/{safe_name}_Leads.xlsx"

            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                workbook  = writer.book
                worksheet = writer.sheets['Sheet1']

                for i, col in enumerate(df.columns):
                    max_len = max(
                        df[col].astype(str).map(len).max(), 
                        len(str(col)) 
                    ) + 2
                    
                    worksheet.set_column(i, i, max_len)
            
            print(f"\n✅ SUCCESS! Saved {len(Data_Scraped)} leads to:\n{filename}")
        else:
            print("\n❌ No data collected.")

if __name__ == "__main__":
    scrape_google_maps()

