from fastapi import FastAPI, File, UploadFile
from app.storage import upload_file
from app.ai_processing import detect_objects
import requests
import firebase_admin
from firebase_admin import credentials, db
from typing import List

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://forensic360-85087-default-rtdb.firebaseio.com"}
)

app = FastAPI()

@app.post("/upload-images/")
async def upload_images(files: List[UploadFile]):
    """
    Upload multiple images and save their Firebase URLs in Realtime Database.
    """
    uploaded_files = []

    for file in files:
        result = upload_file(file)  # Upload to Firebase Storage
        if "error" in result:
            return result

        uploaded_files.append(result["file_url"])

    # Store image URLs under a new crime scene record
    crime_scene_ref = db.reference("/crime_scenes").push()
    crime_scene_ref.set({"images": uploaded_files})

    return {"crime_scene_id": crime_scene_ref.key, "uploaded_images": uploaded_files}


@app.post("/process-images/")
async def process_images(files: List[UploadFile]):
    """
    Upload multiple images, run AI detection on each, and store in Firebase.
    """
    processed_results = []

    for file in files:
        result = upload_file(file)  # Upload to Firebase Storage
        if "error" in result:
            return result

        # Download the image from Firebase
        response = requests.get(result["file_url"])
        image_path = f"temp_{file.filename}"
        with open(image_path, "wb") as f:
            f.write(response.content)

        # Run AI detection
        detections = detect_objects(image_path)

        processed_results.append({
            "file_url": result["file_url"],
            "detections": detections
        })

    # Store processed results in Firebase
    crime_scene_ref = db.reference("/crime_scenes").push()
    crime_scene_ref.set({"processed_images": processed_results})

    return {"crime_scene_id": crime_scene_ref.key, "processed_results": processed_results}
