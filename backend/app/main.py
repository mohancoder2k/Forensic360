from fastapi import FastAPI, File, UploadFile
from app.storage import upload_file
from app.ai_processing import detect_objects
import requests

app = FastAPI()

@app.post("/upload-image/")
async def upload_image(file: UploadFile):
    """Uploads an image and returns its Firebase URL."""
    result = upload_file(file)
    return result


@app.post("/process-image/")
async def process_image(file: UploadFile):
    """Uploads an image, runs AI detection, and returns detected objects."""
    result = upload_file(file)
    if "error" in result:
        return result

    # Download the image from Firebase for processing
    response = requests.get(result["file_url"])
    image_path = f"temp_{file.filename}"
    with open(image_path, "wb") as f:
        f.write(response.content)

    detections = detect_objects(image_path)

    return {"file_url": result["file_url"], "detections": detections}