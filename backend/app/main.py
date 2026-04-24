from pathlib import Path
from typing import List
import os

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .ml import get_mllm_service
from .models import Embedding, Photo
from .schemas import PhotoOut, SearchRequest, SearchResponse
from .utils import cosine_similarity, save_upload, structured_score, vector_to_json, json_to_vector

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Photo Album API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

def to_photo_out(photo: Photo, score=None) -> PhotoOut:
    return PhotoOut(
        id=photo.id,
        file_url=f"/uploads/{Path(photo.file_path).name}",
        original_name=photo.original_name,
        caption=photo.caption or "",
        scene=photo.scene or "",
        weather=photo.weather or "",
        people=photo.people or "",
        actions=photo.actions or "",
        objects=photo.objects or "",
        mood=photo.mood or "",
        score=score,
    )

@app.get("/")
def root():
    return {"message": "Photo Album API is running."}

@app.get("/photos", response_model=List[PhotoOut])
def list_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).order_by(Photo.id.desc()).all()
    return [to_photo_out(p) for p in photos]

async def _store_uploaded_file(file: UploadFile, db: Session):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"{file.filename}: only image files are allowed.")

    content = await file.read()
    saved_path = save_upload(file.filename, content)

    service = get_mllm_service()
    analysis = service.analyze(saved_path)

    photo = Photo(
        file_path=saved_path,
        original_name=file.filename,
        caption=analysis["caption"],
        scene=analysis["scene"],
        weather=analysis["weather"],
        people=analysis["people"],
        actions=analysis["actions"],
        objects=analysis["objects"],
        mood=analysis["mood"],
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    embedding = Embedding(
        photo_id=photo.id,
        vector=vector_to_json(analysis["embedding"]),
    )
    db.add(embedding)
    db.commit()
    db.refresh(photo)
    return photo

@app.post("/upload", response_model=PhotoOut)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    photo = await _store_uploaded_file(file, db)
    return to_photo_out(photo)

@app.post("/upload-multiple", response_model=List[PhotoOut])
async def upload_multiple_images(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one image.")
    uploaded = []
    for file in files:
        photo = await _store_uploaded_file(file, db)
        uploaded.append(to_photo_out(photo))
    return uploaded

@app.post("/search", response_model=SearchResponse)
def search_images(payload: SearchRequest, db: Session = Depends(get_db)):
    service = get_mllm_service()
    query_vec = service.text_embedding(payload.query)

    photos = db.query(Photo).all()
    scored = []

    for photo in photos:
        if not photo.embedding:
            continue
        photo_vec = json_to_vector(photo.embedding.vector)
        semantic = cosine_similarity(query_vec, photo_vec)
        structure = structured_score(payload.query, photo)
        total = 0.85 * semantic + 0.15 * structure
        scored.append((photo, round(float(total), 4)))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = [to_photo_out(photo, score=score) for photo, score in scored[:payload.top_k]]
    return SearchResponse(query=payload.query, results=results)

@app.get("/image/{photo_id}", response_model=PhotoOut)
def get_image(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return to_photo_out(photo)

@app.delete("/photo/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")

    file_path = photo.file_path
    if photo.embedding:
        db.delete(photo.embedding)

    db.delete(photo)
    db.commit()

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    return {"message": "Photo deleted successfully.", "photo_id": photo_id}
