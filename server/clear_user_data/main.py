from google.cloud import firestore
import firebase_admin
from firebase_admin import storage

from utils.Utilities import api_key_required, CORS_HEADERS

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(options={"storageBucket": "puurlee.appspot.com"})

# Initialize Firestore
db = firestore.Client()

# To deploy:
# gcloud functions deploy clear_user_data --runtime python312 --trigger-http --allow-unauthenticated --entry-point main --service-account=286240844421-compute@developer.gserviceaccount.com --gen2 --set-env-vars API_KEY=your-api-key
# To run locally:
# API_KEY=your-api-key functions-framework --target main --debug


def clear_storage(user_id):
    bucket = storage.bucket()
    location = f"uploads/{user_id}/"
    blob = bucket.blob(location)
    blobs = bucket.list_blobs(prefix=location)

    # Delete each file
    for blob in blobs:
        print(f"Deleting {blob.name}")
        blob.delete()


def clear_firestore(user_id):
    # Query all documents with matching user_id
    docs = db.collection("documents").where("user_id", "==", user_id).stream()

    delete_count = 0
    for doc in docs:
        doc.reference.delete()
        delete_count += 1

    print(f"Deleted {delete_count} documents for user_id '{user_id}'.")


@api_key_required
def clear_user_data(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        try:
            user_id = request.form.get("user_id")
            clear_storage(user_id)
            clear_firestore(user_id)
            response_body = f"Data for {user_id} removed successfully."
            return (response_body, 200, CORS_HEADERS)

        except Exception as e:
            print(e)
            response_body = f"Error inserting file data: {e}"
            return (response_body, 500, CORS_HEADERS)

    return ("Invalid request method", 405, CORS_HEADERS)


# Entry point for Google Cloud Function
def main(request):
    return clear_user_data(request)
