from fastapi import UploadFile
from app.config import bucket

def upload_file(file: UploadFile):
    """Uploads a file to Firebase Storage and returns its public URL."""
    try:
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file, content_type=file.content_type)
        blob.make_public()  # Make the file publicly accessible
        return {"file_url": blob.public_url}
    except Exception as e:
        return {"error": str(e)}
