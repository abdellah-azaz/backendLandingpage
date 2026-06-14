import os
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from botocore.config import Config

# Load environment variables
load_dotenv()

app = FastAPI(title="Crypton Landing Page Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the landing page domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# S3 Configuration
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
STORAGE_ACCESS_KEY_ID = os.getenv("STORAGE_ACCESS_KEY_ID")
STORAGE_SECRET_ACCESS_KEY = os.getenv("STORAGE_SECRET_ACCESS_KEY")
STORAGE_LINUX_PATH = os.getenv("STORAGE_LINUX_PATH")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=STORAGE_ENDPOINT,
    aws_access_key_id=STORAGE_ACCESS_KEY_ID,
    aws_secret_access_key=STORAGE_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1" # Often required even if ignored by some providers
)

@app.get("/signe")
async def get_signed_url():
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": STORAGE_BUCKET,
                "Key": STORAGE_LINUX_PATH,
            },
            ExpiresIn=3600,  # URL valid for 1 hour
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
