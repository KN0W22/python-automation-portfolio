# 🚀 Python Automation & Web Scraping Portfolio

Hi, I'm a **Python Developer** specializing in **Web Scraping**, **Data Extraction**, and **Browser Automation**.

This repository contains three production-ready projects demonstrating my ability to build bots that collect data, manage assets, and monitor live web metrics for business intelligence.

---

## 📂 Project 1: E-Commerce Asset Migration Bot
**Goal:** Automate the extraction of product data and media for e-commerce stores (e.g., WooCommerce/Shopify migrations).

* **Target Site:** `scrapeme.live` (Simulated E-commerce Store)
* **Tech Stack:** `Playwright`, `Requests`, `Pandas`, `Urllib`
* **Key Features:**
    * **Smart Pagination:** Automatically detects and navigates through multiple pages of products.
    * **Price Filtering:** Logic to identify and extract only specific items (e.g., items under $50).
    * **Asset Management:** Automatically downloads high-resolution product images and saves them to a local directory with sanitized filenames.
    * **Data Export:** Saves product details (Title, Price, Image Path) to a clean CSV file.

---

## 📂 Project 2: B2B Lead Generation & Directory Scraper
**Goal:** Scrape tabular data from business directories to generate high-quality sales leads.

* **Target Site:** `scrapethissite.com` (Hockey Team Database)
* **Tech Stack:** `Requests`, `Pandas`, `BeautifulSoup`, `OpenPyXL`
* **Key Features:**
    * **Table Extraction:** Uses Pandas to instantly convert HTML tables into structured DataFrames.
    * **Automated Pagination:** Loops through directory pages to build a complete master database.
    * **"High-Ticket" Filtering:** Applies business logic to separate raw data from "Qualified Leads" (e.g., filtering teams with > 300 Wins).
    * **Excel Reporting:** Exports two distinct files: a `Raw_Data.xlsx` for records and a `Qualified_Leads.xlsx` for the sales team.

---

## 📂 Project 3: Real-Time Live Data Monitor
**Goal:** Monitor dynamic websites for critical data changes without API access.

* **Target Site:** `worldometers.info` (Live Population Counter)
* **Tech Stack:** `Playwright`, `BeautifulSoup`, `Time`
* **Key Features:**
    * **Dynamic Scraping:** Handles JavaScript-heavy sites where data updates live without page reloads.
    * **Change Detection:** Runs an infinite loop to monitor specific metrics every 2 seconds.
    * **Growth Alert System:** Compares current data vs. historical memory to detect and print alerts when significant growth occurs.
    * **Efficiency:** Uses a single browser session to minimize bandwidth usage (no constant refreshing).

---

## 🛠️ How to Run These Scripts

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/python-automation-portfolio.git](https://github.com/YOUR_USERNAME/python-automation-portfolio.git)
    ```
2.  **Install dependencies:**
    ```bash
    pip install playwright pandas requests beautifulsoup4 openpyxl
    playwright install
    ```
3.  **Run a script (example):**
    ```bash
    python "Asset_Downloader_Bot/The Asset Scraper.py"
    ```

---

## 📬 Contact Me
I am currently open for freelance work in **Data Extraction**, **Lead Generation**, and **Automation**.

* **Email: junmarcgahilomo@gmail.com**
* **GitHub: https://github.com/KN0W22**
