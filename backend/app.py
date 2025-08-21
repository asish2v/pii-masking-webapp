import io
import os
import re
import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import easyocr
import spacy

# -------------------------
# FastAPI app + CORS
# -------------------------
app = FastAPI(title="PII Masker Backend (EN+HI)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# One-time model loads (speed)
# -------------------------
# EasyOCR: Hindi + English only
reader = easyocr.Reader(['hi', 'en'], gpu=False)

# SpaCy: English NER (names, dates, locations, orgs)
# Make sure you've run: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

# -------------------------
# Regex patterns (India)
# -------------------------
PATTERNS = {
    # Aadhaar: 4 4 4 or 12 digits
    "aadhaar": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b"),
    # PAN: 5 letters + 4 digits + 1 letter
    "pan": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    # Phone: 10 digits starting 6-9
    "phone": re.compile(r"\b[6-9]\d{9}\b"),
    # DOB: DD/MM/YYYY or DD-MM-YYYY
    "dob": re.compile(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"),
    # Email
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b"),
}

# Hindi/Devanagari & basic English words commonly seen on IDs
DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]+")  # Hindi text
# Named entity labels we consider PII-like
PII_ENT_LABELS = {"PERSON", "GPE", "LOC", "ORG", "DATE"}

def looks_like_pii(text: str) -> bool:
    """Return True if text matches PII patterns or SpaCy NER suggests PII."""
    t = text.strip()
    if not t:
        return False

    # Regex checks
    for _, pat in PATTERNS.items():
        if pat.search(t):
            return True

    # SpaCy NER for English text (names, orgs, places, dates)
    doc = nlp(t)
    for ent in doc.ents:
        if ent.label_ in PII_ENT_LABELS:
            return True

    # If Hindi script present and the word is long enough, likely name/address token
    if DEVANAGARI_RANGE.search(t) and len(t) >= 3:
        return True

    return False


def expand_bbox(bbox, pad=4):
    """
    EasyOCR returns 4-point bbox: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    We convert to padded rectangle (x_min,y_min,x_max,y_max).
    """
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    x_min, x_max = int(min(xs)), int(max(xs))
    y_min, y_max = int(min(ys)), int(max(ys))
    return max(x_min - pad, 0), max(y_min - pad, 0), x_max + pad, y_max + pad


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Accepts an image, OCRs in Hindi+English, detects PII with regex+SpaCy,
    and draws black boxes over PII regions. Returns masked PNG.
    """
    data = await file.read()

    # Decode to image
    np_img = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse({"detail": "Invalid image"}, status_code=400)

    # Optional: scale down very large images for speed (keeps aspect)
    max_side = 1600
    h, w = img.shape[:2]
    scale = 1.0
    if max(h, w) > max_side:
        scale = max_side / float(max(h, w))
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    # OCR (bbox, text, prob)
    results = reader.readtext(img)

    # Mask any region that looks like PII
    for (bbox, text, prob) in results:
        if prob < 0.4:  # drop very low-confidence detections
            continue
        if looks_like_pii(text):
            x1, y1, x2, y2 = expand_bbox(bbox, pad=6)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)

    # Encode back to PNG and stream
    ok, enc = cv2.imencode(".png", img)
    if not ok:
        return JSONResponse({"detail": "Encoding failed"}, status_code=500)

    return StreamingResponse(io.BytesIO(enc.tobytes()), media_type="image/png")
