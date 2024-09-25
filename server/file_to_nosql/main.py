import time
from google.cloud import documentai_v1 as documentai
from google.cloud import firestore
import firebase_admin
from firebase_admin import storage

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(options={
    'storageBucket': 'puurlee.appspot.com'
})

# Initialize Firestore
db = firestore.Client()

# To deploy:
# gcloud functions deploy file_to_nosql --runtime python312 --trigger-http --allow-unauthenticated --entry-point main --service-account=286240844421-compute@developer.gserviceaccount.com --gen2
# To run locally:
# functions-framework --target main --debug

def upload_to_storage(file, user_id):
    try:
        bucket = storage.bucket()
        location = f'uploads/{user_id}/{file.filename}'
        blob = bucket.blob(location)
        blob.upload_from_file(file, content_type=file.content_type)
        storage_url = f"{bucket}/{location}"
        
        return storage_url
    except Exception as e:
        print(f'An error occurred during file upload: {e}')
        return None
    
def extract_text_with_documentai(file_bytes, mime_type):
    # info from: https://console.cloud.google.com/ai/document-ai/locations/us/processors/7cbb0c206b7a5176/details?hl=en&project=puurlee&supportedpurview=project
    project_id = "286240844421" # os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = 'us'  # Format is 'us' or 'eu'
    processor_id = "7cbb0c206b7a5176"

    client = documentai.DocumentProcessorServiceClient()

    name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'

     # Read the file file into memory
    raw_document = documentai.RawDocument(content=file_bytes, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    # Process the document
    result = client.process_document(request=request)

    # Extract the text from the document
    document = result.document
    
    html_content = convert_to_html_with_formatting(extract_text_with_layout(document))

    return html_content


def extract_text_with_layout(document):
    """
    Extracts text from the Document AI response, while preserving layout information.
    """
    text = document.text
    
    # Iterate over each page in the document
    layout_text = []
    for page in document.pages:
        page_text = []
        for paragraph in page.paragraphs:
            paragraph_text = []
            for line in paragraph.layout.text_anchor.text_segments:
                line_text = text[line.start_index:line.end_index]
                paragraph_text.append(line_text)
            
            # Join paragraph text and add it to the page text
            page_text.append(" ".join(paragraph_text))
        
        # Join page text and add it to the layout text
        layout_text.append("\n".join(page_text))

    # Join all pages' text
    full_text = "\n\n".join(layout_text)
    return full_text

def convert_to_html_with_formatting(text):
    """
    Convert extracted text to basic HTML format with paragraphs and line breaks.
    """
    # Escape any HTML special characters (optional)
    escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Replace line breaks with HTML <br> and paragraphs with <p> tags
    html_content = "<html><body>"
    paragraphs = escaped_text.split("\n\n")  # Assume paragraphs are separated by double line breaks
    for paragraph in paragraphs:
        if paragraph.strip():  # Only wrap non-empty paragraphs
            html_content += f"<p>{paragraph.replace('\n', '<br>')}</p>"
    html_content += "</body></html>"

    return html_content

def get_text(layout, document):
    """
    Helper function to extract text given a layout and document object
    """
    response_text = ''
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response_text += document.text[start_index:end_index]
    return response_text

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

def file_to_nosql(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600',
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
    }

    if request.method == 'POST':
        try:
            print(request)
            # Read the uploaded file file
            file = request.files['file']
            file_data = file.read()
            file.seek(0)
            mime_type = file.mimetype
            
            print(f"File is {len(file_data)} bytes" )
            print(mime_type)

            # Extract text using Document AI
            extracted_text = extract_text_with_documentai(file_data, mime_type)

            storage_url = upload_to_storage(file, request.form.get("user_id"))

            # Structure the data
            structured_data = structure_data(extracted_text, storage_url, request)

            # Insert structured data into Firestore
            doc_ref = insert_into_firestore(structured_data)

            return f"Data inserted successfully with ID: {doc_ref[1].id}", 200

        except Exception as e:
            print(e)
            return f"Error: {str(e)}", 500

    return "Invalid request method", 405

# Entry point for Google Cloud Function
def main(request):
    return file_to_nosql(request)


