
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder

from datetime import datetime, timezone
import shutil
import os

from auth import router as auth_router, get_current_user
from database import scans_collection
from yolo_service import MedicalYOLOService
from cnn_service import predict_cnn


app = FastAPI(
    title="MRI Suspicious Region Detection API",
    description="CNN classification and YOLO suspicious-region detection",
    version="1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


# Folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "../uploads"))
DETECTION_FOLDER = os.path.join(BASE_DIR, "static", "detections")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECTION_FOLDER, exist_ok=True)


# YOLO model
detector = MedicalYOLOService(
    os.path.join(BASE_DIR, "../models/best.pt")
)


# Serve annotated images
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)


@app.get("/")
def home():
    return {"message": "MRI Detection API is running"}


# Analyze and save a scan
@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an image."
        )

    # Prevent directory traversal through filenames
    filename = os.path.basename(file.filename)

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Save the image for YOLO
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # CNN classification
        cnn_result = predict_cnn(contents)

        # YOLO region detection
        yolo_result = detector.analyze_scan(file_path)

        # Prepare results for MongoDB
        scan_record = {
            "user_id": user["_id"],
            "filename": filename,
            "cnn_result": jsonable_encoder(cnn_result),
            "yolo_result": jsonable_encoder(yolo_result),
            "created_at": datetime.now(timezone.utc),
        }

        # Save the completed analysis
        saved_scan = scans_collection.insert_one(scan_record)

        # Preserve the response fields used by the existing frontend
        return JSONResponse(
            content=jsonable_encoder({
                "scan_id": str(saved_scan.inserted_id),
                "filename": filename,
                "result": yolo_result,
                "cnn_result": cnn_result,
                "created_at": scan_record["created_at"],
            })
        )

    except HTTPException:
        raise
    except Exception:
        # Log the actual error in the backend terminal for debugging
        import logging
        logging.exception("Scan analysis or database saving failed")
        raise HTTPException(
            status_code=500,
            detail="Analysis or saving failed. Please try again."
        )
    finally:
        await file.close()


# Retrieve the logged-in user's scan history
@app.get("/history")
def get_scan_history(user=Depends(get_current_user)):
    try:
        scans = scans_collection.find(
            {"user_id": user["_id"]}
        ).sort("created_at", -1)

        history = []

        for scan in scans:
            history.append({
                "scan_id": str(scan["_id"]),
                "filename": scan.get("filename"),
                "cnn_result": scan.get("cnn_result"),
                "yolo_result": scan.get("yolo_result"),
                "created_at": (
                    scan["created_at"].isoformat()
                    if scan.get("created_at")
                    else None
                ),
            })

        return {"scans": history}

    except Exception:
        import logging
        logging.exception("Could not retrieve scan history")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve scan history."
        )
