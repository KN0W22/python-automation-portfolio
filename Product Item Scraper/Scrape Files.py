import json
import glob
import os
import csv

all_products = []

base_path = r"C:\Users\junma\Python Code\Python-Automation-Portfolio\Product Item Scraper"

output_folder = os.path.join(base_path, "Scrape CSVs")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

csv_columns = ['itemid', 'shopid', 'name', 'image', 'price', 'stock', 'rating_star', 'cmt_count']

json_files = glob.glob('Product Item Scraper/Data to Scrape/*.json')

print(f"Found {len(json_files)} JSON file(s)")

for json_file in json_files:
    print(f"\nProcessing: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'items' in data:
        all_products = data['items']
    else:
        all_products = []
    
    print(f"Loaded {len(all_products)} products")
    
    json_filename = os.path.basename(json_file).replace('.json', '.csv')
    csv_file = os.path.join(output_folder, json_filename)
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        
        for product in all_products:
            item_basic = product.get('item_basic', {})
            item_rating = product.get('item_rating', {})
            
            row = {
                'itemid': item_basic.get('itemid', ''),
                'shopid': item_basic.get('shopid', ''),
                'name': item_basic.get('name', ''),
                'image': item_basic.get('image', ''),
                'price': item_basic.get('price', ''),
                'stock': item_basic.get('stock', ''),
                'rating_star': item_rating.get('rating_star', ''),
                'cmt_count': item_rating.get('cmt_count', '')
            }
            writer.writerow(row)
    
    print(f"CSV saved to: {csv_file}")
