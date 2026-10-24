from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import router as auth_router
import shutil
import os

from yolo_service import MedicalYOLOService
from cnn_service import predict_cnn


# Create FastAPI application
app = FastAPI(
    title="MRI Suspicious Region Detection API",
    description="YOLO-based suspicious region localization",
    version="1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

# =========================
# Folder paths
# =========================

UPLOAD_FOLDER = "../uploads"
DETECTION_FOLDER = "static/detections"


# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECTION_FOLDER, exist_ok=True)


# =========================
# YOLO Model
# =========================

detector = MedicalYOLOService("../models/best.pt")


# =========================
# Serve annotated images
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================
# Home endpoint
# =========================

@app.get("/")
def home():

    return {
        "message": "MRI Detection API is running"
    }


# =========================
# Analyze image
# =========================


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Read the uploaded image once
    contents = await file.read()

    # Save the image for YOLO detection
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Member 1: CNN classification (Real or Fake)
    cnn_result = predict_cnn(contents)

    # Existing Member 2: YOLO suspicious-region detection
    yolo_result = detector.analyze_scan(file_path)

    # Return both results to the frontend
    return JSONResponse(content={
        "filename": file.filename,
        "result": yolo_result,
        "cnn_result": cnn_result
    })
