from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from googlesearch import search
import pandas as pd
import os
import time
import random
import requests
import urllib3
import re 

# --- CONFIGURATION ---
SAFE_MODE = True
output_folder = "Leads"
filename = f"{output_folder}/High_Ticket_Leads.xlsx"

def get_incremented_filename(path):
    """
    If `path` exists, return a new filename with an incremented suffix
    before the extension: High_Ticket_Leads.xlsx -> High_Ticket_Leads2.xlsx
    """
    # Logic: Check if file exists, if not return original path. If it does exist,
    # increment a counter suffix (2, 3, 4...) until finding an unused filename.
    dirpath, base = os.path.split(path)
    name, ext = os.path.splitext(base)
    # If the original doesn't exist, just return it
    if not os.path.exists(path):
        return path
    counter = 2
    while True:
        candidate = os.path.join(dirpath, f"{name}{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def choose_output_file(folder, default_filepath):
    # Logic: Loop through user choices to either append to existing .xlsx files
    # or create a new file with auto-incremented naming if collision occurs.
    default_basename = os.path.basename(default_filepath)

    # Ensure folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Gather existing Excel files in the folder
    files = [f for f in os.listdir(folder) if f.lower().endswith('.xlsx')]

    while True:
        print('\n📁 Save Options:')
        print('  1) Append to an existing file')
        print('  2) Create a new file (auto-increment if name exists)')
        choice = input('Choose 1 or 2 (default 2): ').strip() or '2'

        if choice == '1':
            if not files:
                print(' ⚠️ No existing .xlsx files found in folder. Please choose option 2 to create a new file.')
                continue

            print('\nAvailable files:')
            for idx, f in enumerate(files, 1):
                print(f"  {idx}) {f}")
            sel = input('Enter the number of the file to append to, or enter a full path: ').strip()

            # If user enters a number
            if sel.isdigit():
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(files):
                    chosen = os.path.join(folder, files[sel_idx])
                    if os.path.exists(chosen):
                        return chosen
                    else:
                        print(' ⚠️ Selected file no longer exists. Refreshing list...')
                        files = [f for f in os.listdir(folder) if f.lower().endswith('.xlsx')]
                        continue
                else:
                    print(' ⚠️ Invalid selection. Try again.')
                    continue

            # Treat input as path
            if os.path.exists(sel):
                return sel
            else:
                print(' ⚠️ Path not found. Try again.')
                continue

        elif choice == '2':
            name = input(f'Enter new filename (default "{default_basename}"): ').strip() or default_basename
            candidate = os.path.join(folder, name)
            candidate = get_incremented_filename(candidate)
            print(f'✅ New file will be: {candidate}')
            return candidate

        else:
            print(' ⚠️ Invalid choice. Please enter 1 or 2.')


if not os.path.exists(output_folder):
    os.makedirs(output_folder)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- PART 0: THE SALES BRAIN ---
def get_sales_angle(issues_string):
    """Translates technical errors into sales pitches."""
    # Logic: Convert website audit issues into persuasive sales messages that highlight
    # problems (no website, broken site, mobile unfriendly, insecure, slow) to justify outreach.
    # Provide a sensible fallback when no specific issues were detected
    if not issues_string:
        return "Website needs modernization."
    
    if "No Website" in issues_string:
        return "Invisible on Google search, losing local leads daily."
    if "Parked" in issues_string or "Broken" in issues_string:
        return "Dead site = dead inbound leads."
    if "Not Mobile Friendly" in issues_string:
        return "Over 60% of users can't use this site properly."
    if "Not Secure" in issues_string:
        return "Trust issue – visitors bounce before calling."
    if "Slow Load Time" in issues_string:
        return "Slow load kills conversions and rankings."
        
    return "Website needs modernization."

# --- PART 1: WEBSITE AUDIT & EMAIL HUNTER ---
def audit_Website(url):
    # Logic: Fetch the website and check for red flags (bad status, no HTTPS, slow load time,
    # not mobile-friendly, parked/under construction). Extract emails from page content.
    # Detect tech stack (WordPress, Wix, Squarespace, Shopify). Return None if no issues found.
    if not url.startswith('http'):
        url = 'http://' + url

    result = {
        "url": url, 
        "is_bad": False, 
        "issues": [], 
        "emails": "Email Not Found", 
        "tech_stack": "HTML"
    }
    start_time = time.time()
    
    try:
        response = requests.get(
            url, 
            timeout=10, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            verify=False 
        )
        load_time = time.time() - start_time
        
        # 1. CHECK STATUS
        if response.status_code != 200:
            result["is_bad"] = True
            result["issues"].append(f"Broken Link (Status {response.status_code})")
            return result

        if not response.url.startswith("https"):
            result["is_bad"] = True
            result["issues"].append("Not Secure (No HTTPS)")

        if load_time > 5.0:
            result["is_bad"] = True
            result["issues"].append(f"Slow Load Time ({round(load_time, 2)}s)")

        # 2. ANALYZE CONTENT
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text().lower()
        html_content = str(response.content).lower()

        # Mobile Check
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            result["is_bad"] = True
            result["issues"].append("Not Mobile Friendly")

        # Parked Check
        red_flags = ["under construction", "index of /", "domain parked", "coming soon"]
        if any(flag in page_text for flag in red_flags):
            result["is_bad"] = True
            result["issues"].append("Parked/Construction Page")

        # --- 📧 EMAIL HUNTER ---
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text))
        if emails:
            result["emails"] = ", ".join(emails)

        # --- 🛠️ TECH STACK DETECTOR ---
        if "wp-content" in html_content: result["tech_stack"] = "WordPress"
        elif "wix.com" in html_content: result["tech_stack"] = "Wix"
        elif "squarespace" in html_content: result["tech_stack"] = "Squarespace"
        elif "shopify" in html_content: result["tech_stack"] = "Shopify"

    except Exception as e:
        result["is_bad"] = True
        error_msg = str(e).split('(')[0]
        result["issues"].append(f"Site Error: {error_msg}")

    if result["is_bad"] or result["emails"] != "Email Not Found":
        return result
    else:
        return None

# --- PART 2: VERIFICATION LOGIC (For 'No Website' Leads) ---
def verify_lead_quality(lead):
    # Logic: For leads without a website, perform a Google search to find their official site.
    # If a site is found, audit it for issues. If audit fails (bad site), mark as good lead.
    # If no site found after search, mark as "truly no website" (good lead). Return False if good site found.
    name = lead["Business Name"]
    address = lead["City/Address"]
    query = f"{name} {address} official website"
    
    print(f"   🔎 Verifying: {name}...", end="")

    while True:
        try:
            if SAFE_MODE: time.sleep(random.uniform(2, 4))
            
            results = search(query, num_results=5, advanced=True)
            found_official_site = False
            
            for result in results:
                url = result.url
                if any(x in url for x in ["facebook", "instagram", "yelp", "linkedin", "yellowpages"]):
                    continue
                
                print(f" Found site: {url}")
                found_official_site = True
                
                audit = audit_Website(url)
                if audit:
                    lead["Website"] = url
                    lead["Audit Issues"] = "; ".join(audit["issues"])
                    lead["Audit Status"] = "Bad (Found via Search)"
                    lead["Sales Angle"] = get_sales_angle(lead["Audit Issues"])
                    lead["Business Email"] = audit["emails"]
                    lead["Tech Stack"] = audit["tech_stack"]
                    print(f" ✅ Bad website! Email: {audit['emails']}")
                    return True
                else:
                    print(" ❌ Good website found - Skipping.")
                    return False
            
            if not found_official_site:
                print(" ✅ Verified! (Truly No Website)")
                lead["Audit Status"] = "No Website"
                lead["Sales Angle"] = "Invisible on Google search."
                lead["Business Email"] = "Email Not Found"
                lead["Tech Stack"] = "N/A"
                return True 

        except Exception as e:
            if "429" in str(e):
                print("\n🛑 GOOGLE IP BAN. Pausing...")
                input("⌨️  Reset Internet & Press ENTER...")
                continue
            return False

# --- PART 3: SMART EXCEL SAVING ---
def save_and_format_excel(filename, new_lead_data):
    # Logic: Append new lead to existing Excel file (or create new file), deduplicate by phone number,
    # limit duplicate URLs to 5 rows max, apply formatting (headers, column widths, text wrapping).
    # Use xlsxwriter for styling and openpyxl for row height auto-adjustment.
    
    # 1. Prepare Data
    new_df = pd.DataFrame([new_lead_data])

    # Sanitize: Remove newline chars so cells can wrap properly
    for col in new_df.columns:
        if new_df[col].dtype == object:
            new_df[col] = new_df[col].astype(str).str.replace(r'[\n\r]+', ' ', regex=True)

    # 2. Append to existing data
    if os.path.exists(filename):
        try:
            existing_df = pd.read_excel(filename)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["Phone Number"], keep="last", inplace=True)
        except:
            combined_df = new_df
    else:
        combined_df = new_df

    # 3. Detect link columns
    link_cols = [c for c in combined_df.columns if "link" in c.lower() or "website" in c.lower()]
    if not link_cols:
        for col in combined_df.columns:
            try:
                if combined_df[col].astype(str).str.contains(r"http://|https://|www\.", regex=True).any():
                    link_cols.append(col)
            except Exception:
                continue

    # 4. Limit to a maximum of 5 rows per unique link-group
    if link_cols:
        combined_df = combined_df.groupby(link_cols, group_keys=False).apply(lambda g: g.head(5)).reset_index(drop=True)

    # 5. Write with XlsxWriter Engine
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        combined_df.to_excel(writer, index=False, sheet_name='Leads')
        workbook = writer.book
        worksheet = writer.sheets['Leads']

        # Formats
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'align': 'left'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})

        # Apply Headers
        for col_num, value in enumerate(combined_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Apply Column Sizes
        for i, col_name in enumerate(combined_df.columns):
            col_name = str(col_name)
            if "Link" in col_name or "Website" in col_name:
                worksheet.set_column(i, i, 15, wrap_format)
            elif "Angle" in col_name or "Issues" in col_name:
                worksheet.set_column(i, i, 50, wrap_format)
            elif "Name" in col_name or "Address" in col_name or "Email" in col_name:
                worksheet.set_column(i, i, 30, wrap_format)
            else:
                worksheet.set_column(i, i, 20, wrap_format)

    # 6. Post-process with openpyxl
    try:
        from openpyxl import load_workbook
        from openpyxl.styles import Alignment
        import math

        wb = load_workbook(filename)
        ws = wb.active

        nonlink_idx = [i + 1 for i, col in enumerate(combined_df.columns) if col not in link_cols]

        for row_idx in range(2, ws.max_row + 1):
            max_lines = 1
            for col_idx in nonlink_idx:
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.alignment = Alignment(wrapText=True, vertical='top')
                text = str(cell.value) if cell.value is not None else ""
                lines = max(1, math.ceil(len(text) / 50))
                if lines > max_lines:
                    max_lines = lines

            ws.row_dimensions[row_idx].height = max(15, max_lines * 15)

        wb.save(filename)
    except Exception as e:
        print(f"⚠️ Warning: couldn't auto-adjust Excel formatting: {e}")

# --- PART 4: ROBUST SCRAPING LOGIC ---
def extract_data_from_panel(page, link_url):
    # Logic: Wait for Google Maps business panel to load, then extract business details
    # (name, category, website, phone, address) using CSS selectors and data attributes.
    try:
        # Wait for SPECIFIC Business Title Class
        page.wait_for_selector("h1.DUwDvf", timeout=5000)
        
        name_loc = page.locator("h1.DUwDvf").first
        if not name_loc.is_visible(): return None
        name = name_loc.inner_text()
        
        # Safe extractions
        category = "No Category"
        if page.locator('button[jsaction*=".category"]').count() > 0:
            category = page.locator('button[jsaction*=".category"]').first.inner_text()
        
        website_url = None
        if page.locator('a[data-item-id="authority"]').count() > 0:
            website_url = page.locator('a[data-item-id="authority"]').first.get_attribute("href")
        
        phone = "No Phone"
        if page.locator('button[data-item-id^="phone:"]').count() > 0:
            phone_loc = page.locator('button[data-item-id^="phone:"]').first
            phone = phone_loc.get_attribute("aria-label").replace("Phone: ", "")
        
        address = "No Address"
        if page.locator('button[data-item-id="address"]').count() > 0:
            addr_loc = page.locator('button[data-item-id="address"]').first
            address = addr_loc.get_attribute("aria-label").replace("Address: ", "")

        # --- FIX APPLIED HERE: Direct assignment to "Website" ---
        return {
            "Business Name": name,
            "Category": category,
            "Phone Number": phone,
            "City/Address": address,
            "Google Maps Link": link_url,
            "Website": website_url 
        }
    except Exception as e:
        return None
    
def scrape_google_maps(target_keyword, quantity):
    # Logic: Launch Playwright browser, search Google Maps for a keyword, scroll through results
    # to load enough listings, click each result to extract business panel data. Return list of raw leads.
    raw_leads = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        print(f"\n🚀 Starting Scrape for: '{target_keyword}'")
        page.goto("https://www.google.com/maps", timeout=60000)
        
        try:
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)
            sb = page.get_by_role("textbox").first
            if not sb.is_visible(): sb = page.locator("input").first
            sb.click()
            sb.fill(target_keyword)
            page.keyboard.press("Enter")
            
            try: page.wait_for_selector('div[role="feed"], h1', timeout=20000)
            except: 
                print("   ❌ No results loaded.")
                browser.close()
                return []
                
        except: 
            browser.close()
            return []

        # List View
        if page.locator('div[role="feed"]').is_visible():
            print(" 📜 List View detected. Scrolling...")
            page.hover('div[role="feed"]')
            prev_cnt = 0
            retries = 0
            while True:
                page.mouse.wheel(0, 3000)
                time.sleep(2)
                curr_cnt = page.locator("a[href*='/maps/place/']").count()
                if curr_cnt >= quantity: break
                if curr_cnt == prev_cnt:
                    retries += 1
                    if retries >= 3: break
                else:
                    retries = 0
                    prev_cnt = curr_cnt
            
            count = min(quantity, curr_cnt)
            links = page.locator("a[href*='/maps/place/']").all()[:count]
            print(f" 🔍 Found {len(links)} locations. Processing...")
            
            for i, link in enumerate(links):
                try:
                    link.scroll_into_view_if_needed()
                    link.click()
                    time.sleep(2) 
                    current_url = page.url 
                    data = extract_data_from_panel(page, current_url)
                    
                    if data: 
                        raw_leads.append(data)
                        print(f"   [{i+1}/{count}] Extracted: {data['Business Name']}")
                except: continue

        # Single Result
        elif page.locator("h1").is_visible():
            print(" 🎯 Single Result detected.")
            data = extract_data_from_panel(page, page.url)
            if data: raw_leads.append(data)
        
        else: print(" ❌ No results.")
        
        browser.close()
        return raw_leads

# --- PART 5: MAIN CONTROLLER ---
def main():
    # Logic: Prompt user for search keywords, leads per keyword, and country filter.
    # For each keyword, scrape Google Maps, audit websites (or verify no-website leads),
    # filter by country (if specified), and save qualified leads to Excel with deduplication.
    print("\n--- 🚀 Google Maps High-Ticket Engine ---")
    user_input = input("\n📝 Enter keywords: ")
    keywords = [k.strip() for k in user_input.split(',') if k.strip()]
    if not keywords: return
    amount = int(input("🔢 Leads per keyword? (Rec: 20): "))
    country_filter = input("🌍 Restrict leads to country (leave blank for no restriction): ").strip()

    # Ask whether to append to an existing file or create a new one
    out_filename = choose_output_file(output_folder, filename)
    print(f"✅ Using output file: {out_filename}")

    for i, keyword in enumerate(keywords):
        print(f"\n\n📢 --- BATCH {i+1}: '{keyword}' ---")
        leads = scrape_google_maps(keyword, amount)
        print(f"📊 Found {len(leads)} candidates. Processing...")

        saved_count = 0
        for lead in leads:
            # Deduplicate
            if os.path.exists(out_filename):
                try:
                    existing = pd.read_excel(out_filename)
                    if str(lead["Phone Number"]) in existing["Phone Number"].astype(str).values:
                        print(f" ⏭️ Skipping {lead['Business Name']} (Duplicate)")
                        continue
                except: pass

            is_good = False
            
            # --- FIX APPLIED HERE: Branch A uses 'Website' ---
            # BRANCH A: Website Exists -> Audit it
            if lead["Website"]:
                print(f"   🌐 Auditing Map Link...")
                audit = audit_Website(lead["Website"])
                if audit:
                    # lead["Website"] is already set, no need to copy
                    lead["Audit Issues"] = "; ".join(audit["issues"])
                    lead["Audit Status"] = "Bad (Map Link)"
                    lead["Sales Angle"] = get_sales_angle(lead["Audit Issues"])
                    lead["Business Email"] = audit["emails"]
                    lead["Tech Stack"] = audit["tech_stack"]
                    print(f"   ✅ Bad Site! Email: {audit['emails']} | Phone: {lead['Phone Number']}")
                    is_good = True
                else: print("   ❌ Site is Good. Skipping.")

            # BRANCH B: No Website -> Verify "Ghost" status
            else:
                is_good = verify_lead_quality(lead)

            # SAVE (Using New Smart Formatter)
            if is_good:
                # Country filter: if specified and not found in address, skip
                if country_filter:
                    addr = lead.get("City/Address", "") or ""
                    if country_filter.lower() not in addr.lower():
                        print(f"   🛑 Skipping {lead['Business Name']} (Outside {country_filter})")
                        continue

                # Ensure Business Email and Sales Angle defaults so Excel cells are not blank
                if not lead.get("Business Email"):
                    lead["Business Email"] = "Email Not Found"
                if not lead.get("Sales Angle"):
                    lead["Sales Angle"] = get_sales_angle(lead.get("Audit Issues", ""))

                saved_count += 1
                save_and_format_excel(out_filename, lead)
                print(f"   💾 Saved: {lead['Business Name']}")
            
            time.sleep(random.uniform(5, 12)) 

        if i < len(keywords) - 1:
            print(f"\n😴 Break time...")
            time.sleep(random.randint(60, 120))

if __name__ == "__main__":
    main()