import os
import pandas as pd
import requests

URL = "http://127.0.0.1:8000/ebook/api/upload-bulk/"

EXCEL_FILE = "ebook_pdf.xlsx"
COVERS_FOLDER = "ebook_pdf_image/"
PDFS_FOLDER = "ebook_pdf/"


def upload_books():
    # -----------------------------
    # Check required files/folders
    # -----------------------------
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Excel file '{EXCEL_FILE}' not found.")
        return

    if not os.path.exists(COVERS_FOLDER):
        print(f"❌ Cover folder '{COVERS_FOLDER}' not found.")
        return

    if not os.path.exists(PDFS_FOLDER):
        print(f"❌ PDF folder '{PDFS_FOLDER}' not found.")
        return


    image_lookup = {}

    for filename in os.listdir(COVERS_FOLDER):
        name, ext = os.path.splitext(filename)

        if ext.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            image_lookup[name.strip().lower()] = filename

    # -------------------------------------------------------
    # Scan PDF folder once
    # -------------------------------------------------------
    pdf_lookup = {}

    for filename in os.listdir(PDFS_FOLDER):
        name, ext = os.path.splitext(filename)

        if ext.lower() == ".pdf":
            pdf_lookup[name.strip().lower()] = filename

    # -------------------------------------------------------
    # Read Excel
    # -------------------------------------------------------
    df = pd.read_excel(EXCEL_FILE)
    df = df.fillna("")

    print(f"Found {len(df)} books.\n")

    # -------------------------------------------------------
    # Upload Loop
    # -------------------------------------------------------
    for index, row in df.iterrows():

        title = str(row.get("Book Title")).strip()
        author = str(row.get("Author")).strip()

        if not title:
            print(f"⚠️ Row {index+1}: Empty title. Skipping.")
            continue

        key = title.lower()

        # ---------------- Image ----------------
        if key not in image_lookup:
            print(f"❌ Row {index+1}: Cover not found for '{title}'")
            continue

        # ---------------- PDF ----------------
        if key not in pdf_lookup:
            print(f"❌ Row {index+1}: PDF not found for '{title}'")
            continue

        image_name = image_lookup[key]
        pdf_name = pdf_lookup[key]

        image_path = os.path.join(COVERS_FOLDER, image_name)
        pdf_path = os.path.join(PDFS_FOLDER, pdf_name)

        print(f"🔎 Found:")
        print(f"   Image -> {image_name}")
        print(f"   PDF   -> {pdf_name}")

        payload = {
            "title": title,
            "author": author,
        }

        # Detect image MIME type
        _, ext = os.path.splitext(image_name)

        ext = ext.lower()

        if ext == ".jpg":
            content_type = "image/jpeg"
        elif ext == ".jpeg":
            content_type = "image/jpeg"
        elif ext == ".png":
            content_type = "image/png"
        elif ext == ".webp":
            content_type = "image/webp"
        else:
            content_type = "application/octet-stream"

        try:
            with open(image_path, "rb") as img_file, open(pdf_path, "rb") as pdf_file:

                files = {
                    "cover_image": (
                        image_name,
                        img_file,
                        content_type,
                    ),
                    "pdf_file": (
                        pdf_name,
                        pdf_file,
                        "application/pdf",
                    ),
                }

                response = requests.post(
                    URL,
                    data=payload,
                    files=files,
                )

                if response.status_code == 201:
                    print(f"   ✅ Uploaded '{title}'")

                else:
                    try:
                        print(f"   ❌ {response.json()}")
                    except:
                        print(f"   ❌ {response.text}")

        except Exception as e:
            print(f"   💥 Network error: {e}")


if __name__ == "__main__":
    upload_books()