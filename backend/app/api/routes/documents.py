from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.session import get_db

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "data" / "raw_pdfs"


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    crop: str | None = Form(default=None),
    region: str | None = Form(default=None),
    source: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    target = UPLOAD_DIR / safe_name
    target.write_bytes(await file.read())
    doc = Document(
        title=title or safe_name,
        source=source,
        crop=crop,
        region=region,
        file_path=str(target),
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"message": "Document uploaded", "document_id": doc.id}


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return docs
