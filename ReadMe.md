# 🧠 Image Processing API (Assembli Take-Home)

This is a minimal FastAPI-based image processing service designed for uploading and QAing computer vision datasets. It mimics a simplified version of tools like FiftyOne.

## ✅ Features

- Scans all images in the `pics/` folder
- Uses a pretrained ResNet18 to:
  - Auto-tag each image (ImageNet labels)
  - Extract metadata (width, height, format)
  - Generate an embedding vector
- Saves all data into a local SQLite database (`image_metadata.db`)

---

## 🔧 Step-by-Step Usage

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

or install manually

```bash
pip install fastapi uvicorn pillow torch torchvision requests
```

### 2. Place Your Images

Add the images you want to process into the `pics/` directory.  
Example:

You can use any common image format (`.jpg`, `.jpeg`, `.png`, `.webp`, etc.).

---

### 3. Start the API Server

Run the following command from the root directory of your project:

```bash
python main.py
```

### 4. Trigger the Folder Scan

```bash
curl http://localhost:6000/process-folder
```

### 5. View results in local db

`image_metadata.db`
