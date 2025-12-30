import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os

base_path = r"C:\Users\junma\Python Code\Python-Automation-Portfolio\Lead_Generation_Bot"
output_folder = os.path.join(base_path, "Hockey_Teams_Data")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

base_url = "https://www.scrapethissite.com/pages/forms/"
all_teams = []
page_num = 1

print("Starting the Directory Scraper...")

while True:
    print(f"Scraping Page {page_num}...")
    
    url = f"{base_url}?page_num={page_num}"
    
    response = requests.get(url)
    
    tables = pd.read_html(response.text)
    current_table = tables[0]
    
    all_teams.append(current_table)
    
    soup = BeautifulSoup(response.text, "html.parser")
    next_button = soup.find("a", attrs={"aria-label": "Next"})
    
    if next_button:
        page_num += 1
        time.sleep(1) 
    else:
        print("Reached the last page. Stopping.")
        break

print("Combining all pages...")
master_df = pd.concat(all_teams, ignore_index=True)

print(f"Total Teams Scraped: {len(master_df)}")

qualified_leads = master_df[master_df["Wins"] > 50]

print(f"Found {len(qualified_leads)} High-Performing Teams.")

file_path_all = os.path.join(output_folder, "all_hockey_teams.xlsx")
master_df.to_excel(file_path_all, index=False)

file_path_winning = os.path.join(output_folder, "winning_teams_only.xlsx")
qualified_leads.to_excel(file_path_winning, index=False)

print(f"✅ Data delivered to: {output_folder}")