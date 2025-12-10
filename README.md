# 🌐 SmartExtract AI – Intelligent Document Extraction & Approval System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248?style=flat&logo=mongodb&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

SmartExtract AI is an AI-powered automation platform for extracting structured fields from procurement & RFP documents (PDF/DOCX) using *Gemini + RAG* without OCR. The system provides an editable dashboard for verification and approval, and stores finalized documents in a searchable database.

## 🌟 Features

### Core System Capabilities

- 📄 **Document Upload** (PDF & DOCX)
- 🤖 **AI-Based Field Extraction** (Gemini 2.5 Flash + RAG)
- 🧾 **Extracts procurement fields like:**
  - Title, File Number, Bid Deadline
  - Vendor & Contact Information
  - Addresses, Signatures, Emails, Phone numbers and more
- ✏️ **Editable Dashboard** for manual corrections
- ✔️ **Approval Workflow** — approved documents saved to DB
- 📂 **Approved Documents Listing** with Search
- 📊 **Analytics Dashboard** with stats & real-time updates

### User Experience

- 🎨 Modern UI with animated dashboards
- ⚡ Instant AI Processing
- 🔍 Advanced search & filter
- 💾 MongoDB storage with automatic timestamps

## 🛠️ Tech Stack

### Backend
- **FastAPI**
- **Python 3.10+**
- **MongoDB**
- **Gemini 2.5 Flash**
- **uuid, Pydantic, CORS**

### Frontend
- **HTML / Bootstrap 5**
- **Vanilla JavaScript**
- **Responsive UI & Sidebar Layout**

### Document Processing
- **docx2txt** for .docx
- **PyPDF2** for .pdf
- **Gemini extraction** (no OCR)

## 📁 Project Structure

```
SmartExtract-AI/
│
├── backend/
│   ├── main.py                     # FastAPI backend
│   ├── database.py                 # MongoDB connection
│   ├── extract.py                  # PDF / DOCX parser
│   ├── gemini_client.py            # Gemini AI integration
│   ├── models.py                   # Pydantic models
│   ├── requirements.txt            # Dependencies
│   └── uploads/                    # Temporary file storage
│
└── frontend/
    ├── index.html                  # Upload Page
    ├── dashboard.html              # Editable document view
    └── results.html                # Approved docs listing
```

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/hariteja007/SmartExtract-AI.git
cd SmartExtract-AI/backend
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 4️⃣ Add Gemini API Key

Edit:
```
backend/gemini_client.py
```

Replace:
```python
GEMINI_API_KEY = "YOUR_KEY_HERE"
```

### 5️⃣ Start Backend

```bash
uvicorn main:app --reload
```

Runs at: **http://127.0.0.1:8000**

### 6️⃣ Open Frontend

Open `frontend/index.html` in browser

## 🧪 Sample API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload and extract fields |
| `/documents/latest` | GET | Get last uploaded draft |
| `/documents/{id}` | GET | Fetch by ID |
| `/documents/{id}/approve` | PUT | Approve document |
| `/documents/approved` | GET | List approved |

## 📦 Requirements

```
fastapi
uvicorn
pymongo
google-generativeai
python-multipart
PyPDF2
docx2txt
pydantic
```

## 🎯 Usage Flows

### 1. Upload → Extract
User uploads PDF/DOCX → AI extracts fields

### 2. Dashboard Edit
Editable fields for manual verification

### 3. Approve
Stores approved version to database

### 4. View Approved
Search and open from results page

## 🔮 Future Enhancements

- [ ] Add user authentication (Admin / Reviewer)
- [ ] Integrated PDF viewer in dashboard
- [ ] Export to Excel / PDF
- [ ] Cloud deployment (Render / Vercel / Railway)
- [ ] Vector DB support for enhanced RAG

## 🤝 Contribution

```bash
git checkout -b feature/XYZ
git commit -m "Added XYZ"
git push origin feature/XYZ
```

## 📝 License

MIT License — Free for personal & academic usage

## ⭐ Support

If you like this project, give it a ⭐ on GitHub 🙏

**https://github.com/hariteja007/SmartExtract-AI**

## 💚 Credits

Built with dedication by **Hari Teja**

For enterprise procurement automation & AI innovation 🧠🚀
