import cv2
import os
import json
from datetime import datetime
from ultralytics import YOLO

# 🔹 Load YOLOv8 model
model = YOLO("yolov8n.pt")

# 🔹 Folder containing crime scene images
IMAGE_FOLDER = r"D:\Crime Scene"
OUTPUT_FOLDER = r"D:\Output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🔹 Define forensic labels
FORENSIC_LABELS = {
    0: "person",
    2: "gun",
    3: "blood_spatter",  # Custom mapping (requires fine-tuning)
    4: "bullet_hole"
}

def generate_forensic_analysis(image_name):
    """Simulated forensic analysis for blood spatter and bullet trajectory."""
    return {
        "image": image_name,
        "analysis": {
            "blood_spatter": {
                "impact_velocity": "Medium (5-15 m/s)",
                "impact_angle": "45°",
                "droplet_size": "2-5 mm (Medium)",
                "distance_from_source": "1.2 meters",
                "surface_type": "Non-porous (Smooth)",
                "confidence": "High"
            },
            "bullet_trajectory": {
                "gun_type": "Handgun (9mm)",
                "bullet_speed": "350 m/s",
                "entry_wound": "Upper torso, right side",
                "exit_wound": "Lower back, left side",
                "shooting_distance": "4 meters",
                "wind_speed": "Insufficient data",
                "confidence": "Medium"
            }
        },
        "timestamp": str(datetime.now())
    }

def detect_objects_in_crime_scene(image_folder):
    """Processes crime scene images and returns forensic analysis in JSON format."""
    json_results = []

    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)

        if image is None:
            print(f"[❌] Could not load image: {image_name}")
            continue

        # 🔹 Run YOLOv8 detection
        results = model(image_path)

        # 🔹 Draw bounding boxes for detected objects
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                label = model.names[class_id] if class_id in model.names else FORENSIC_LABELS.get(class_id, "unknown")

                # 🔹 Choose color for the bounding box
                color = (0, 255, 0) if label == "gun" else (0, 0, 255) if label == "blood_spatter" else (255, 0, 0)

                # 🔹 Draw bounding box & label
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{label} ({conf:.2f})", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 🔹 Save processed image
        output_path = os.path.join(OUTPUT_FOLDER, f"detected_{image_name}")
        cv2.imwrite(output_path, image)
        print(f"[✔] Processed: {image_name} -> {output_path}")

        # 🔹 Generate JSON forensic analysis
        forensic_analysis = generate_forensic_analysis(image_name)
        json_results.append(forensic_analysis)

    # 🔹 Save JSON Report
    json_output_path = os.path.join(OUTPUT_FOLDER, "crime_scene_analysis.json")
    with open(json_output_path, "w") as json_file:
        json.dump(json_results, json_file, indent=4)

    print(f"\n✅ Forensic analysis completed! JSON report saved at: {json_output_path}")

# 🔹 Run detection and generate forensic analysis
detect_objects_in_crime_scene(IMAGE_FOLDER)
