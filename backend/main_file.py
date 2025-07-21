from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
from uuid import uuid4
from PIL import Image
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import uvicorn

# Create app
app = FastAPI()

# Image folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load pretrained model
model = models.resnet18(pretrained=True)
model.eval()

# Load imagenet class labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels_path = "imagenet_classes.txt"
if not os.path.exists(labels_path):
    import requests
    with open(labels_path, "w") as f:
        f.write(requests.get(LABELS_URL).text)
with open(labels_path) as f:
    labels = [line.strip() for line in f.readlines()]

# Transform function
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_id = str(uuid4())
        filepath = os.path.join(UPLOAD_FOLDER, file_id + os.path.splitext(file.filename)[1])
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Open image
        image = Image.open(filepath).convert("RGB")
        img_tensor = transform(image).unsqueeze(0)

        # Predict
        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs, 1)
            label = labels[predicted.item()]

        return JSONResponse({
            "filename": file.filename,
            "tag": label
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6000, reload=True)
