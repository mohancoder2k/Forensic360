import firebase_admin
from firebase_admin import credentials, storage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase Admin SDK initialization
cred = credentials.Certificate("firebase_credentials.json")  # Correct filename
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
})

# Reference to Firebase Storage
bucket = storage.bucket()
