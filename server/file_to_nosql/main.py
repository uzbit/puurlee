
import time
import csv
import pytesseract
from io import BytesIO, StringIO
from PIL import Image
from pdf2image import convert_from_bytes

from google.cloud import firestore
import firebase_admin
from firebase_admin import storage
from utils.Utilities import api_key_required, CORS_HEADERS

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(options={
    'storageBucket': 'puurlee.appspot.com'
})

# Initialize Firestore
db = firestore.Client()

# To build docker container:
# From root
# docker build -f file_to_nosql/Dockerfile -t file_to_nosql .

# To run docker container:
# From root
# docker run -v ./service_account.json:/app/service_account.json:ro -e GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json" -p 8080:8080 file_to_nosql

# To call service:
# curl -X POST \
#   -F file=@test/jpg/page1.jpg \
#   http://localhost:8080

# To deploy:
# gcloud functions deploy file_to_nosql --runtime python312 --trigger-http --allow-unauthenticated --entry-point main --service-account=286240844421-compute@developer.gserviceaccount.com --gen2 --set-env-vars API_KEY=your-api-key
# To run locally:
# API_KEY=your-api-key functions-framework --target main --debug

def upload_to_storage(file, user_id):
    bucket = storage.bucket()
    location = f'uploads/{user_id}/{file.filename}'
    blob = bucket.blob(location)
    blob.upload_from_file(file, content_type=file.content_type)
    storage_url = f"{bucket}/{location}" 
    return storage_url


def extract_table_data_tesseract_from_bytes(image_data):
    """
    Performs OCR on the given image bytes using Tesseract in TSV mode (PSM 6),
    reads the output, and groups text by line.
    Returns a list of lines, where each line is a concatenation of
    (left-sorted) text tokens.
    """

    # 1. Convert the raw image bytes into a PIL Image
    img = Image.open(BytesIO(image_data))

    # 2. Run Tesseract in TSV mode directly in memory
    #    --psm 6 is often good for block/column text
    tsv_data = pytesseract.image_to_data(
        img,
        config="--psm 6",
        output_type=pytesseract.Output.STRING,
    )

    # 3. Parse the TSV data
    lines_data = {}  # line_num -> list of (left, text)
    tsv_io = StringIO(tsv_data)
    reader = csv.DictReader(tsv_io, delimiter="\t", quoting=csv.QUOTE_NONE)

    # Tesseract TSV columns (typical for Tesseract 4+):
    # level, page_num, block_num, par_num, line_num,
    # word_num, left, top, width, height, conf, text
    for row in reader:
        # Skip rows that aren't level=5 (word level)
        if row["level"] != "5":
            continue
        text = row["text"].strip()
        if not text:
            continue

        line_num = int(row["line_num"])
        left = int(row["left"])

        if line_num not in lines_data:
            lines_data[line_num] = []

        # Collect (left, text) so we can sort tokens left-to-right if needed
        lines_data[line_num].append((left, text))

    # 4. Build an output structure
    #    Sort each line’s tokens by the left coordinate
    extracted_lines = []
    for line_num in sorted(lines_data.keys()):
        tokens_in_line = sorted(lines_data[line_num], key=lambda x: x[0])
        line_text = " ".join(token[1] for token in tokens_in_line)
        extracted_lines.append(line_text)

    return extracted_lines

# def convert_to_html_with_formatting(text):
#     """
#     Convert extracted text to basic HTML format with paragraphs and line breaks.
#     """
#     # Escape any HTML special characters (optional)
#     escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

#     # Replace line breaks with HTML <br> and paragraphs with <p> tags
#     html_content = "<html><body>"
#     paragraphs = escaped_text.split("\n\n")  # Assume paragraphs are separated by double line breaks
#     for paragraph in paragraphs:
#         if paragraph.strip():  # Only wrap non-empty paragraphs
#             html_content += f"<p>{paragraph.replace('\n', '<br>')}</p>"
#     html_content += "</body></html>"

#     return html_content
    
def structure_data(text, storage_url, request):
    # For simplicity, we'll structure the data as a simple dictionary
    structured_data = {
        "timestamp": time.time(),
        "content": text,
        "user_id": request.form.get("user_id"),
        "storage_url": storage_url,
    }
    return structured_data

def insert_into_firestore(data):
    # Insert the structured data into Firestore
    doc_ref = db.collection("documents").add(data)
    return doc_ref

@api_key_required
def file_to_nosql(request):
    
    if request.method == 'OPTIONS':
        # For preflight requests
        return ('', 204, CORS_HEADERS)

    if request.method == 'POST':
        try:
            print(request)
            # Read the uploaded file file
            file = request.files['file']
            file_data = file.read()
            file.seek(0)
            mime_type = file.mimetype
            
            print(f"File is {len(file_data)} bytes and type: {mime_type}" )
            print(mime_type)

            extracted_text = []
            if mime_type == "application/pdf":
                pages = convert_from_bytes(file_data)
                for i, page_data in enumerate(pages, start=1):
                    extracted_text += extract_table_data_tesseract_from_bytes(page_data)
            else:        
                extracted_text = extract_table_data_tesseract_from_bytes(file_data)

            storage_url = upload_to_storage(file, request.form.get("user_id"))

            # Structure the data
            structured_data = structure_data(extracted_text, storage_url, request)

            # Insert structured data into Firestore
            doc_ref = insert_into_firestore(structured_data)
            response_body = f"Data inserted successfully with ID: {doc_ref[1].id}"
            return (response_body, 200, CORS_HEADERS)

        except Exception as e:
            print("ERROR:", e)
            response_body = f"Error inserting file data."
            return (response_body, 500, CORS_HEADERS)

    return ("Invalid request method", 405, CORS_HEADERS)

# Entry point for Google Cloud Function
def main(request):
    return file_to_nosql(request)


