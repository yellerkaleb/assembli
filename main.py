from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
from uuid import uuid4
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import sqlite3
import json

app = FastAPI()

# Paths
UPLOAD_FOLDER = "pics"
DB_PATH = "image_metadata.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load pretrained model
from torchvision.models import resnet18, ResNet18_Weights
weights = ResNet18_Weights.DEFAULT
model = resnet18(weights=weights)
model.eval()

# Load ImageNet class labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels_path = "imagenet_classes.txt"
if not os.path.exists(labels_path):
    import requests
    with open(labels_path, "w") as f:
        f.write(requests.get(LABELS_URL).text)
with open(labels_path) as f:
    labels = [line.strip() for line in f.readlines()]

# Image transform
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Init SQLite DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    filename TEXT,
    tag TEXT,
    metadata TEXT,
    embedding TEXT
)
''')
conn.commit()
conn.close()

# Helper to extract embedding vector
def get_embedding(tensor):
    embedding_layer = torch.nn.Sequential(*list(model.children())[:-1])  # Remove final layer
    with torch.no_grad():
        embedding = embedding_layer(tensor).squeeze().tolist()
    return embedding

# Process all images in folder
@app.get("/process-folder")
def process_folder():
    results = []
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            image = Image.open(filepath).convert("RGB")
            img_tensor = transform(image).unsqueeze(0)

            with torch.no_grad():
                outputs = model(img_tensor)
                _, predicted = torch.max(outputs, 1)
                label = labels[predicted.item()]
                embedding = get_embedding(img_tensor)

            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
            }

            image_id = str(uuid4())
            c.execute("INSERT OR REPLACE INTO images (id, filename, tag, metadata, embedding) VALUES (?, ?, ?, ?, ?)",
                      (image_id, filename, label, json.dumps(metadata), json.dumps(embedding)))
            results.append({"filename": filename, "tag": label})

        except Exception as e:
            results.append({"filename": filename, "error": str(e)})

    conn.commit()
    conn.close()
    return JSONResponse(results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=6000, reload=True)
