# Intelligent Web-based Photo Album

This project implements the capstone idea:

> An intelligent web-based photo album with automatic image understanding and natural language retrieval using multimodal large language models.

## Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Database:** SQLite
- **Models:** BLIP (captioning) + CLIP (embeddings)

## Features

- Upload photos through a web interface
- Automatically generate:
  - image caption
  - structured tags
  - image embedding
- Store metadata in a database
- Search photos with natural language
- Hybrid ranking:
  - semantic vector similarity
  - structured attribute match

## Folder structure

```text
photo_album_capstone/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick start

### 1. Start backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Start frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

### 3. Open browser

Frontend:
`http://127.0.0.1:5173`

Backend docs:
`http://127.0.0.1:8000/docs`

## Database schema

### photos
- id
- file_path
- original_name
- caption
- scene
- weather
- people
- actions
- objects
- mood

### embeddings
- photo_id
- vector

## Suggested capstone upgrades

1. Replace SQLite JSON vector storage with **pgvector/PostgreSQL**
2. Replace keyword-derived structured fields with **LLaVA or GPT-4o vision JSON extraction**
3. Add **user login and per-user albums**
4. Add **tag editing, delete, and favorites**
5. Add **evaluation pipeline**:
   - Recall@K
   - Precision@K
   - mAP
   - query case study analysis

## Important note

This codebase is a complete working prototype, but the first run requires model downloads from Hugging Face.
If your laptop is weak, you can switch to smaller models or keep embeddings precomputed.
