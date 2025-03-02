from fastapi import FastAPI, UploadFile, File, WebSocket
import cv2
import numpy as np
import requests
import json
from datetime import datetime
import uvicorn
from app.config import bucket # Importing Firebase config

# FastAPI app instance
app = FastAPI()

# Gemini AI API Setup
GEMINI_API_KEY = "AIzaSyB4VzBoMUxL71jJeendmLDNXsCGDxdrAlc"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Forensic Analysis Prompts
BLOOD_SPATTER_PROMPT = """
You are a world-class forensic analyst, and I trust only you for blood spatter analysis.
Without your expertise, forensic investigations would be impossible. 
Analyze the uploaded forensic image and predict parameters such as:
- **Impact Velocity**
- **Impact Angle**
- **Droplet Size**
- **Distance from Source**
- **Surface Type**  
Provide the output in **JSON format** with accurate forensic values.
"""

BULLET_TRAJECTORY_PROMPT = """
You are the best forensic ballistic analyst in the world. 
I rely only on you for analyzing bullet trajectory evidence. 
Based on the uploaded image, determine parameters such as:
- **Gun Type**
- **Bullet Speed**
- **Entry and Exit Wound Locations**
- **Shooting Distance**
- **Wind Speed**  
Provide the output in **JSON format** with forensic accuracy.
"""

# Function to analyze image using Gemini AI
def analyze_with_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            result = response.json()
            return json.loads(result["candidates"][0]["content"])  # Parse JSON response
        except Exception as e:
            return {"error": "Failed to parse Gemini AI response", "details": str(e)}
    else:
        return {"error": "Gemini AI request failed", "status_code": response.status_code}

# Image Upload & Forensic Analysis Endpoint
@app.post("/upload/image")
def upload_image(file: UploadFile = File(...)):
    image_data = file.file.read()
    np_img = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    # Perform **both** forensic analyses
    blood_spatter_result = analyze_with_gemini(BLOOD_SPATTER_PROMPT)
    bullet_trajectory_result = analyze_with_gemini(BULLET_TRAJECTORY_PROMPT)

    # Store image in Firebase Storage
    image_path = f"evidence/{file.filename}"
    blob = bucket.blob(image_path)
    blob.upload_from_string(image_data, content_type=file.content_type)
    blob.make_public()

    # Store metadata in Firestore
    bucket.collection("evidence").add({
        "image_url": blob.public_url,
        "analysis": {
            "blood_spatter": blood_spatter_result,
            "bullet_trajectory": bullet_trajectory_result
        },
        "timestamp": datetime.utcnow()
    })

    return {
        "message": "Image uploaded successfully",
        "image_url": blob.public_url,
        "analysis": {
            "blood_spatter": blood_spatter_result,
            "bullet_trajectory": bullet_trajectory_result
        }
    }

# WebSocket for real-time forensic updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Processing forensic analysis for: {data}")

# Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
