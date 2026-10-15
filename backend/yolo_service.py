"""
yolo_service.py
Integration module for Member 3 (FastAPI / Chatbot Backend).
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO


class MedicalYOLOService:

    def __init__(self, weights_path="../models/best.pt"):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"Model weights not found at: {weights_path}"
            )

        self.model = YOLO(weights_path)

    def analyze_scan(
        self,
        image_path,
        conf_threshold=0.15,
        save_annotated_dir="static/detections"
    ):
        """
        Analyzes an uploaded medical scan for deepfake tampering.
        """

        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(
                f"Unable to load image from {image_path}"
            )

        results = self.model.predict(
            source=img,
            conf=conf_threshold,
            verbose=True
        )[0]

        print("YOLO detections:", len(results.boxes))

        for box in results.boxes:
            print("Confidence:", float(box.conf[0]))

        os.makedirs(save_annotated_dir, exist_ok=True)

        annotated_img = img.copy()
        detections = []

        for box in results.boxes:

            coords = box.xyxy[0].tolist()
            conf = float(box.conf[0])

            x1, y1, x2, y2 = map(int, coords)

            cv2.rectangle(
                annotated_img,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2
            )

            label = f"Tampered: {conf * 100:.1f}%"

            cv2.putText(
                annotated_img,
                label,
                (x1, max(18, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (0, 0, 255),
                2
            )

            detections.append({
                "bounding_box": [x1, y1, x2, y2],
                "confidence": round(conf * 100, 2),
                "classification": "tampered_tumor_region"
            })

        filename = os.path.basename(image_path)

        annotated_path = os.path.join(
            save_annotated_dir,
            f"detected_{filename}"
        )

        cv2.imwrite(annotated_path, annotated_img)

        return {
            "tampering_detected": len(detections) > 0,
            "region_count": len(detections),
            "suspicious_regions": detections,
            "annotated_image_url":
                f"/static/detections/detected_{filename}"
        }


if __name__ == "__main__":

    if os.path.exists("best.pt"):
        detector = MedicalYOLOService("best.pt")
        print("[+] YOLO Service initialized successfully!")