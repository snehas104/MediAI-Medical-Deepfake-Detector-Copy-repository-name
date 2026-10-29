
import os
import uuid
import cv2
from pathlib import Path
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR.parent / "models" / "best.pt"
DEFAULT_OUTPUT_DIR = BASE_DIR / "static" / "detections"


class MedicalYOLOService:
    def __init__(self, weights_path=None):
        self.weights_path = Path(
            weights_path or DEFAULT_MODEL_PATH
        ).resolve()

        if not self.weights_path.is_file():
            raise FileNotFoundError(
                f"YOLO model not found: {self.weights_path}"
            )

        self.model = YOLO(str(self.weights_path))
        print(f"[YOLO] Model loaded: {self.weights_path}")
        print(f"[YOLO] Classes: {self.model.names}")

    def analyze_scan(
        self,
        image_path,
        conf_threshold=0.25,
        save_annotated_dir=None,
    ):
        image_path = Path(image_path).resolve()
        img = cv2.imread(str(image_path))

        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        results = self.model.predict(
            source=img,
            conf=conf_threshold,
            iou=0.45,
            imgsz=640,
            max_det=20,
            verbose=False,
        )[0]

        output_dir = Path(
            save_annotated_dir or DEFAULT_OUTPUT_DIR
        ).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Unique output name prevents concurrent uploads overwriting files.
        output_name = f"detected_{uuid.uuid4().hex}.jpg"
        output_path = output_dir / output_name

        annotated = results.plot()

        if not cv2.imwrite(str(output_path), annotated):
            raise RuntimeError("Failed to save annotated image.")

        detections = []

        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())

            detections.append({
                "class_id": class_id,
                "classification": self.model.names[class_id],
                "confidence": round(confidence * 100, 2),
                "bounding_box": [
                    round(float(v), 2)
                    for v in box.xyxy[0].tolist()
                ],
            })

        return {
            "tampering_detected": len(detections) > 0,
            "region_count": len(detections),
            "suspicious_regions": detections,
            "annotated_image_url": (
                f"/static/detections/{output_name}"
            ),
        }
