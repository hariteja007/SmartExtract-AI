from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uuid

from database import documents_collection
from extract import extract_text_from_file
from gemini_client import extract_fields_from_text
from models import UpdateDocument

app = FastAPI(title="Smart Document Extraction System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    text = extract_text_from_file(file.file, file.filename)
    fields = extract_fields_from_text(text)
    doc_id = str(uuid.uuid4())

    documents_collection.insert_one({
        "_id": doc_id,
        "filename": file.filename,
        "fields": fields,
        "status": "pending",
        "created_at": datetime.utcnow()
    })

    return {"id": doc_id, "fields": fields, "status": "pending"}


# ---------- FIXED ORDER: approved first ----------
@app.get("/documents/approved")
def approved_documents():
    docs = list(documents_collection.find({"status": "approved"}))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


@app.get("/documents/latest")
def latest_document():
    doc = documents_collection.find_one(sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No documents found")
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    doc = documents_collection.find_one({"_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc["_id"] = str(doc["_id"])
    return doc


@app.put("/documents/{doc_id}")
def update_document(doc_id: str, body: UpdateDocument):
    documents_collection.update_one(
        {"_id": doc_id},
        {"$set": {"fields": body.fields}}
    )
    return {"updated": True}


@app.put("/documents/{doc_id}/approve")
def approve_document(doc_id: str):
    result = documents_collection.update_one(
        {"_id": doc_id},
        {"$set": {"status": "approved"}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"approved": True}
