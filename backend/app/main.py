from fastapi import FastAPI, File, UploadFile
from app.storage import upload_file

app = FastAPI()

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    """Uploads a file to Firebase Storage."""
    return upload_file(file)   

@app.get("/")
def home():
    return {"message": "Welcome to Forensic 360 API"}
