from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto("https://www.worldometers.info/world-population/")
        page.wait_for_selector(".rts-counter")

        previous_population = 0 

        while True:
            html = page.content()

            soup = BeautifulSoup(html, "html.parser")
            population_counter_text = soup.find("span", class_="rts-counter").text.strip()
            population_number = int(population_counter_text.replace(",", ""))

            growth = population_number - previous_population
            previous_population = population_number

            if previous_population >= 0 and growth > 5:
               print(f"Significant population growth detected! Growth: {population_counter_text}")
            else:
                print(f"Current World Population: {population_counter_text}")
            
            time.sleep(2)

if __name__ == "__main__":
    run()






