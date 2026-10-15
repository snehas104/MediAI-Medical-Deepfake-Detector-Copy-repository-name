from yolo_service import MedicalYOLOService


# Create YOLO detector
detector = MedicalYOLOService("../models/best.pt")


# Test image
image_path = "../uploads/COVID-177.png"


# Analyze image
result = detector.analyze_scan(image_path)


# Display result
print("\n==============================")
print("       YOLO TEST RESULT")
print("==============================")

print("Tampering detected:", result["tampering_detected"])
print("Region count:", result["region_count"])

print("\nSuspicious regions:")

for region in result["suspicious_regions"]:
    print(region)

print("\nAnnotated image:")
print(result["annotated_image_url"])

print("==============================")