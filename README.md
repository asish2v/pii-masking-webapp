# 🔒 PII Masker App

A full-stack application that automatically detects and masks **Personally Identifiable Information (PII)** from uploaded ID card images such as **Aadhaar, PAN, Voter ID, ATM, and College ID cards**.  
The app uses **FastAPI (backend)** + **React (frontend)** + **OCR (EasyOCR)** + **NLP (SpaCy & Regex)**.

---

## ✨ Features

- 📷 Upload any ID card or document (Aadhaar, PAN, Voter ID, College ID, etc.)
- 🤖 Detects **PII** such as:
  - Aadhaar Number
  - PAN Number
  - Names (English + Hindi)
  - Phone Numbers
  - Date of Birth
  - Email IDs
  - Addresses
- 🕶️ Automatically applies **black box masking** over detected text.
- 🎨 Clean **React UI** with theme colors and loading spinner.
- 📥 Option to **download masked image**.
- 🌐 Backend powered by **FastAPI**, OCR with **EasyOCR**, NLP with **SpaCy**.

---

## 🛠️ Tech Stack

- **Frontend**: React (JavaScript, Axios, CSS)
- **Backend**: FastAPI (Python)
- **OCR**: EasyOCR (supports English + Hindi)
- **NLP**: SpaCy + Regex
- **Image Processing**: OpenCV, Pillow

---

## 📂 Project Structure

PII-Masker-App/
│
├── backend/
│ ├── app.py # FastAPI backend
│ ├── requirements.txt # Backend dependencies
│ └── masked/ # Stores processed images
│
├── frontend/
│ ├── src/
│ │ ├── App.js # React frontend
│ │ └── components/ # UI components (upload, loader, etc.)
│ └── package.json # Frontend dependencies
│
└── README.md


---
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app:app --reload

Docs: http://127.0.0.1:8000/docs

---
cd frontend
npm install
npm start

http://localhost:3000


🚀 Usage

Open frontend in browser: http://localhost:3000

Upload an ID card image (Aadhaar, PAN, etc.)

Wait while the backend detects PII (loading spinner shown).

See the black-boxed masked image.

Click Download to save the masked file.


📸 Demo

🔹 Upload Aadhaar → Name & Aadhaar Number masked
🔹 Upload PAN → Name & PAN Number masked
🔹 Upload College ID → Student ID & Name masked