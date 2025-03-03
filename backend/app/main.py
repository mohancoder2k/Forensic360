from fastapi import FastAPI, File, UploadFile
from supabase import create_client, Client
from typing import List
import requests
import os
from app.ai_processing import detect_objects

# Supabase credentials
SUPABASE_URL = "https://azhltddlqwbravaqttsi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6aGx0ZGRscXdicmF2YXF0dHNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5OTIwMTYsImV4cCI6MjA1NjU2ODAxNn0.DScnt9PWzmdOURZ4YJpMyWs7hATvVFCbPJ67piMZ_mo"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPI app
app = FastAPI()

async def upload_to_supabase(file: UploadFile):
    """
    Uploads an image to Supabase Storage and returns the public URL.
    """
    file_path = f"crime_images/{file.filename}"
    
    # Upload file to Supabase Storage
    response = supabase.storage.from_("images").upload(file_path, file.file, {"content-type": file.content_type})
    
    if "error" in response:
        return {"error": response["error"]["message"]}
    
    # Generate public URL
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/images/{file_path}"
    return {"file_url": public_url}

@app.post("/upload-images/")
async def upload_images(files: List[UploadFile]):
    """
    Upload multiple images and store URLs in Supabase PostgreSQL.
    """
    uploaded_files = []

    for file in files:
        result = await upload_to_supabase(file)
        if "error" in result:
            return result
        uploaded_files.append(result["file_url"])

    # Insert image URLs into the database
    data = {"images": uploaded_files}
    response = supabase.table("crime_scenes").insert(data).execute()

    return {"crime_scene_id": response.data[0]["id"], "uploaded_images": uploaded_files}

@app.post("/process-images/")
async def process_images(files: List[UploadFile]):
    """
    Upload images, process them using AI, and store results in Supabase.
    """
    processed_results = []

    for file in files:
        result = await upload_to_supabase(file)
        if "error" in result:
            return result
        
        # Download image from Supabase URL for AI processing
        response = requests.get(result["file_url"])
        image_path = f"temp_{file.filename}"
        with open(image_path, "wb") as f:
            f.write(response.content)

        # Run AI detection
        detections = detect_objects(image_path)
        os.remove(image_path)  # Clean up temp file

        processed_results.append({
            "file_url": result["file_url"],
            "detections": detections
        })

    # Store processed results in Supabase PostgreSQL
    data = {"processed_images": processed_results}
    response = supabase.table("crime_scenes").insert(data).execute()

    return {"crime_scene_id": response.data[0]["id"], "processed_results": processed_results}
