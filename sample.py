import cv2
import os
import json
import requests
from datetime import datetime
from ultralytics import YOLO

# 🔹 Load YOLOv8 model
model = YOLO("yolov8n.pt")

# 🔹 Folders
IMAGE_FOLDER = r"D:\Crime Scene"
OUTPUT_FOLDER = r"D:\Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🔹 Gemini AI API Setup
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # 🔴 Replace with your actual API key
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# 🔹 Forensic Analysis Prompts
BLOOD_SPATTER_PROMPT = """
You are a world-class forensic analyst, and I trust only you for blood spatter analysis.
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

# 🔹 Function to Analyze Image using Gemini AI
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

# 🔹 Function to Detect Objects & Perform Forensic Analysis
def detect_objects_and_analyze(image_folder):
    json_results = []

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)

        if image is None:
            print(f"[❌] Could not load image: {image_name}")
            continue

        # 🔹 Run YOLOv8 detection
        results = model(image_path)

        # 🔹 Save processed image
        output_path = os.path.join(OUTPUT_FOLDER, f"detected_{image_name}")
        cv2.imwrite(output_path, image)
        print(f"[✔] Processed: {image_name} -> {output_path}")

        # 🔹 Generate AI-powered forensic analysis
        blood_analysis = analyze_with_gemini(BLOOD_SPATTER_PROMPT)
        bullet_analysis = analyze_with_gemini(BULLET_TRAJECTORY_PROMPT)

        forensic_analysis = {
            "image": image_name,
            "analysis": {
                "blood_spatter": blood_analysis,
                "bullet_trajectory": bullet_analysis
            },
            "timestamp": str(datetime.now())
        }

        json_results.append(forensic_analysis)

    # 🔹 Save JSON Report
    json_output_path = os.path.join(OUTPUT_FOLDER, "crime_scene_analysis.json")
    with open(json_output_path, "w") as json_file:
        json.dump(json_results, json_file, indent=4)

    print(f"\n✅ AI-Powered Forensic Analysis Completed! JSON report saved at: {json_output_path}")

# 🔹 Run Detection & AI Analysis
detect_objects_and_analyze(IMAGE_FOLDER)
