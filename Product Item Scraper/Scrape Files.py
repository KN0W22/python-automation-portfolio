import json
import glob
import os
import pandas as pd

base_path = os.path.dirname(os.path.abspath(__file__))

output_folder = os.path.join(base_path, "Scrape Excel") 
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

csv_columns = ['Name', 'Price', 'Shop Name', 'Store Location', 'Star Rating']

json_files = glob.glob(os.path.join(base_path, "Data to Scrape", "*.json"))
print(f"Found {len(json_files)} JSON file(s)")

for json_file in json_files:
    print(f"\nProcessing: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        all_products = data
    elif 'items' in data:
        all_products = data['items']
    else:
        all_products = []
    
    print(f"Loaded {len(all_products)} products")
    
    rows_list = []
    
    for product in all_products:
        item_basic = product.get('item_basic', {})
        shop_name = item_basic.get('shop_name', 'N/A')
        raw_price = item_basic.get('price', 0)
        real_price = raw_price / 100000 if raw_price else 0
        item_rating = item_basic.get('item_rating', {})
        star_rating = item_rating.get('rating_star', 0)
        loc = item_basic.get('shop_location', '')
        
        shop_location = loc if loc else "Unknown"

        row = {
            'Name': item_basic.get('name', ''),
            'Price': f"{real_price:,.2f}",
            'Shop Name': shop_name,
            'Store Location': shop_location,
            'Star Rating': f"{star_rating:.1f}"
        }
        rows_list.append(row)

    df = pd.DataFrame(rows_list, columns=csv_columns)

    json_filename = os.path.basename(json_file).replace('.json', '.xlsx')
    excel_file = os.path.join(output_folder, json_filename)
    
    if not df.empty:
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            
            workbook  = writer.book
            worksheet = writer.sheets['Sheet1']
            
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(i, i, max_len)
                
        print(f"✅ Excel saved to: {excel_file}")
    else:
        print(f"⚠️ No data to save for {json_filename}")