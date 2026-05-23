import os
import pandas as pd
import requests

URL = "http://127.0.0.1:8000/api/upload-book/"
EXCEL_FILE = "books.xlsx"
IMAGES_FOLDER = "books_image/"

def upload_inventory():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Excel spreadsheet file '{EXCEL_FILE}' not found.")
        return
        
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: Images folder '{IMAGES_FOLDER}' not found.")
        return

    # 1. Scan the image folder and build a lookup dictionary
    # Example: {'the great gatsby': 'The Great Gatsby.jpeg'}
    image_lookup = {}
    for filename in os.listdir(IMAGES_FOLDER):
        # Split the filename into (name, extension) -> ('The Great Gatsby', '.jpeg')
        name_without_ext, ext = os.path.splitext(filename)
        
        # Lowercase the key to make the search case-insensitive and avoid typos
        image_lookup[name_without_ext.strip().lower()] = filename

    df = pd.read_excel(EXCEL_FILE)
    df = df.fillna('') 

    print(f"Found {len(df)} rows to process. Beginning upload loop...\n")

    for index, row in df.iterrows():
        title = str(row.get('Title')).strip()
        
        if not title:
            print(f"⚠️ Skipping row {index+1}: Empty Title field.")
            continue

        # 2. Search our lookup dictionary for a matching title (case-insensitive)
        title_lower = title.lower()
        
        if title_lower not in image_lookup:
            print(f"❌ Skipping row {index+1} [{title}]: No matching image found with any extension (.png, .jpg, etc.) in '{IMAGES_FOLDER}'")
            continue
            
        # 3. Grab the actual filename with its correct extension from our lookup
        image_name = image_lookup[title_lower]
        image_path = os.path.join(IMAGES_FOLDER, image_name)
        
        print(f"🔎 Found match: '{title}' maps to file '{image_name}'")

        raw_edition = str(row.get('Edition')).strip()
        clean_edition = ''
        if raw_edition != '':
            # Keep only the numeric digits from the text (e.g., "1st" becomes "1", "3rd" becomes "3")
            digits = ''.join(filter(str.isdigit, raw_edition))
            if digits:
                clean_edition = str(int(digits))

        # Map Excel exact column headers to Django model fields
        payload = {
            'title': title,
            'authors': str(row.get('Author(s)')),
            'isbn': str(row.get('ISBN')).strip(),
            'publisher': str(row.get('Publisher')),
            'publication_year': str(int(row.get('Publication Year'))) if row.get('Publication Year') != '' else '',
            
            # Use our new cleaned edition variable here:
            'edition': clean_edition,
            
            'language': str(row.get('Language')).strip(),
            'genre': str(row.get('Genre')).strip(),
            'subject': str(row.get('Subject')).strip() if row.get('Subject') != '' else '',
            'audience': str(row.get('Audience')).strip(),
            'accession_number': str(row.get('Accession Number')).strip(),
            'location_shelf': str(row.get('Location / Shelf')).strip(),
            'number_of_copies': str(int(row.get('Number of Copies'))) if row.get('Number of Copies') != '' else '1',
            'price': str(row.get('Price')),
            'remarks': str(row.get('Remarks')).strip() if row.get('Remarks') != '' else ''
        }

        _, extension = os.path.splitext(image_name)
        clean_ext = extension.replace(".", "").lower() # e.g. "jpeg", "png"
        content_type = f"image/{clean_ext}" if clean_ext != 'jpg' else 'image/jpeg'

        try:
            with open(image_path, 'rb') as img_file:
                files = {
                    'image': (image_name, img_file, content_type) 
                }
                
                response = requests.post(URL, data=payload, files=files)
                
                if response.status_code == 201:
                    print(f"   ✅ Row {index+1}: {response.json().get('message')}")
                else:
                    print(f"   ❌ Row {index+1} Failed: {response.json().get('message')}")
                    
        except Exception as e:
            print(f"   💥 Network error on Row {index+1}: {str(e)}")

if __name__ == "__main__":
    upload_inventory()