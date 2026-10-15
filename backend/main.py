from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import router as auth_router
import shutil
import os

from yolo_service import MedicalYOLOService


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

    # Create path for uploaded image
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # Save uploaded image
    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # Analyze image using YOLO
    result = detector.analyze_scan(file_path)

    return JSONResponse(
        content={
            "filename": file.filename,
            "result": result
        }
    )