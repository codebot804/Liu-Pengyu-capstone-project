# Backend

## Run

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API starts at `http://127.0.0.1:8000`.

## Main endpoints

- `POST /upload` - upload one image and run automatic analysis
- `POST /search` - natural language search
- `GET /photos` - list all photos
- `GET /image/{id}` - get one photo metadata

## Notes

This version uses:
- **BLIP** for image captioning
- **CLIP** for image-text embeddings
- **SQLite** for metadata storage

On first run, Hugging Face models will be downloaded automatically, so the first upload/search can take longer.
