from pydantic import BaseModel
from typing import List, Optional

class PhotoOut(BaseModel):
    id: int
    file_url: str
    original_name: str
    caption: str
    scene: str
    weather: str
    people: str
    actions: str
    objects: str
    mood: str
    score: Optional[float] = None

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class SearchResponse(BaseModel):
    query: str
    results: List[PhotoOut]
