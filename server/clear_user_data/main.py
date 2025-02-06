from google.cloud import firestore
import firebase_admin
from firebase_admin import storage

from utils.Utilities import api_key_required, CORS_HEADERS


## To build docker container:
# From root
# docker build -f clear_user_data/Dockerfile -t clear_user_data .

# To push docker to GC
# From server
# # gcloud auth configure-docker us-central1-docker.pkg.dev
# docker build --platform=linux/amd64 -f clear_user_data/Dockerfile -t gcr.io/puurlee/clear_user_data .
# docker push gcr.io/puurlee/clear_user_data

# To run docker container:
# From root
# docker run -v ./service_account.json:/app/service_account.json:ro -e GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json" -p 8080:8080 clear_user_data

# To call service:
# curl -X POST \
#   -F "file=@test/jpg/page1.jpg" \
#   -F "api_key=key" \
#   https://clear-user-data-286240844421.us-central1.run.app
# http://localhost:8080

# To deploy (NOT WORKING, user UI: https://console.cloud.google.com/run/detail/us-central1/)
# gcloud functions deploy clear_user_data --docker-repository=us-central1-docker.pkg.dev/puurlee/clear_user_data --gen2 --trigger-http --allow-unauthenticated --service-account=286240844421-compute@developer.gserviceaccount.com  --source="gcr.io/puurlee/clear_user_data:latest"
# To run locally:
# functions-framework --target main --debug


# Initialize the Firebase Admin SDK
# firebase_admin.initialize_app(options={"storageBucket": "puurlee.appspot.com"})

# Initialize Firestore
db = firestore.Client()


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
    docs = (
        db.collection("documents")
        .where(field_path="user_id", op_string="==", value=user_id)
        .stream()
    )

    delete_count = 0
    for doc in docs:
        doc.reference.delete()
        delete_count += 1

    print(f"Deleted {delete_count} documents for user_id '{user_id}'.")


def clear_user_data(user_id):
    try:
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
@api_key_required
def main(request):
    if request.method == "OPTIONS":
        # For preflight requests
        return ("", 204, CORS_HEADERS)

    if request.method == "POST":
        user_id = request.form.get("user_id")
        return clear_user_data(user_id)
