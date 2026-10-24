
import io
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms
from torch import nn


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "cnn_model.pth"
CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model(num_classes=2):
    # Must match Member 1's train.py architecture
    model = models.densenet121(
        weights=None
    )
    model.classifier = nn.Linear(
        model.classifier.in_features,
        num_classes
    )
    return model


# Load checkpoint
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"CNN checkpoint not found: {MODEL_PATH}")

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
    weights_only=False
)

class_to_idx = checkpoint.get("class_to_idx", None)

if class_to_idx:
    idx_to_class = {
        int(index): name.capitalize()
        for name, index in class_to_idx.items()
    }
else:
    with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
        saved_names = json.load(f)
    idx_to_class = {
        int(index): name
        for index, name in saved_names.items()
    }

model = build_model(num_classes=len(idx_to_class))
model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()


# Same image size and normalization as the training notebook
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    ),
])


def predict_cnn(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    predicted_index = int(probabilities.argmax().item())

    return {
        "label": idx_to_class[predicted_index],
        "confidence": round(
            float(probabilities[predicted_index].item()), 4
        ),
        "prob_fake": round(float(probabilities[0].item()), 4),
        "prob_real": round(float(probabilities[1].item()), 4),
    }
