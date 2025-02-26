import csv
import google
from google.oauth2 import id_token
import threading
import requests
import time
import pytesseract
from io import BytesIO, StringIO
from PIL import Image
from pdf2image import convert_from_bytes

import firebase_admin
from firebase_admin import storage
from utils.Utilities import (
    structure_data,
    insert_into_firestore,
    api_key_required,
    CORS_HEADERS,
    PUURLEE_API_KEY,
)

# To build docker container:
# From root
# docker build -f file_to_nosql/Dockerfile -t file_to_nosql .

# To push docker to GC
# From server
# # one time: gcloud auth configure-docker us-central1-docker.pkg.dev
# docker build --platform=linux/amd64 -f file_to_nosql/Dockerfile -t gcr.io/puurlee/file_to_nosql .
# docker push gcr.io/puurlee/file_to_nosql

# To run docker container:
# From root
# docker run -v ./service_account.json:/app/service_account.json:ro -e GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json" -p 8080:8080 file_to_nosql

# To call service:
# curl -X POST \
#   -F "file=@test/jpg/test1.jpg" \
#   -F "api_key=key" \
#   -F "user_id=test"
#   https://file-to-nosql-286240844421.us-central1.run.app
# http://localhost:8080

# To deploy (NOT WORKING, user UI: https://console.cloud.google.com/run/detail/us-central1/)
# gcloud functions deploy file_to_nosql --docker-repository=us-central1-docker.pkg.dev/puurlee/file_to_nosql --gen2 --trigger-http --allow-unauthenticated --service-account=286240844421-compute@developer.gserviceaccount.com  --source="gcr.io/puurlee/file_to_nosql:latest"
# To run locally:
# functions-framework --target main --debug

# Task Queue:
#  gcloud projects add-iam-policy-binding 286240844421 --member="serviceAccount:286240844421-compute@developer.gserviceaccount.com" --role="roles/run.invoker"

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(options={"storageBucket": "puurlee.appspot.com"})


def upload_to_storage(file, user_id):
    bucket = storage.bucket()
    location = f"uploads/{user_id}/{file.filename}"
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


def enqueue_embeddings_task(doc_id):
    url = "https://embeddings-286240844421.us-central1.run.app"
    audience = url

    auth_req = google.auth.transport.requests.Request()
    token = id_token.fetch_id_token(auth_req, audience)

    # Build the multipart form-data
    # aiohttp requires a special way to send form fields
    files = {'doc_id': (None, doc_id), 'api_key': (None, PUURLEE_API_KEY)}
    
    headers = {
        "Authorization": f"Bearer {token}",
    }
    def post():
        requests.post(url, headers=headers, files=files)  # ignoring response
    
    # post()
    threading.Thread(target=post, daemon=True).start()
    time.sleep(1)

def file_to_nosql(file, user_id):
    try:
        # Read the uploaded file file
        file_data = file.read()
        file.seek(0)
        mime_type = file.mimetype

        print(f"File is {len(file_data)} bytes and type: {mime_type}")

        extracted_text = []
        if mime_type == "application/pdf":
            pages = convert_from_bytes(file_data)
            for i, page in enumerate(pages, start=1):
                # 1) Create an in-memory buffer
                buffered = BytesIO()

                # 2) Save the PIL image to that buffer in some format (PNG, JPEG, etc.)
                page.save(buffered, format="PNG")

                # 3) Retrieve the raw bytes
                page_data = buffered.getvalue()

                extracted_text += extract_table_data_tesseract_from_bytes(page_data)
        else:
            extracted_text = extract_table_data_tesseract_from_bytes(file_data)

        storage_url = upload_to_storage(file, user_id)

        # Structure the data
        structured_data = structure_data(
            extracted_text, storage_url, user_id, "document"
        )

        # Insert structured data into Firestore
        doc_ref = insert_into_firestore(structured_data)
        doc_id = doc_ref[1].id
        response_body = f"Data inserted successfully with ID: {doc_id}"
        print(response_body)

        # Schedule the embedding async function as a background task
        print("Running embeddings...")
        enqueue_embeddings_task(doc_id)
        print("finished.")
        
        return (response_body, 200, CORS_HEADERS)

    except Exception as e:
        print("ERROR:", e)
        response_body = f"Error inserting file data. {e}"
        return (response_body, 500, CORS_HEADERS)


# Entry point for Google Cloud Function
@api_key_required
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        file = request.files["file"]
        user_id = request.form.get("user_id")

        return file_to_nosql(file, user_id)
