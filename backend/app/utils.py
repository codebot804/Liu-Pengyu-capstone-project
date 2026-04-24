import json
import math
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

SCENE_KEYWORDS = {
    "beach": "beach",
    "sea": "beach",
    "ocean": "beach",
    "mountain": "mountain",
    "forest": "forest",
    "park": "park",
    "city": "city",
    "street": "city",
    "road": "city",
    "indoor": "indoor",
    "room": "indoor",
    "kitchen": "indoor",
    "office": "indoor",
    "school": "school",
    "classroom": "school",
    "restaurant": "restaurant",
    "cafe": "restaurant",
    "home": "home",
    "house": "home",
}

WEATHER_KEYWORDS = {
    "sunny": "sunny",
    "rain": "rainy",
    "raining": "rainy",
    "snow": "snowy",
    "cloud": "cloudy",
    "cloudy": "cloudy",
    "storm": "stormy",
    "fog": "foggy",
}

MOOD_KEYWORDS = {
    "happy": "happy",
    "smile": "happy",
    "smiling": "happy",
    "romantic": "romantic",
    "calm": "calm",
    "peaceful": "calm",
    "excited": "excited",
    "fun": "joyful",
    "party": "joyful",
    "sad": "sad",
}

ACTION_KEYWORDS = {
    "playing": "playing",
    "running": "running",
    "walking": "walking",
    "swimming": "swimming",
    "eating": "eating",
    "driving": "driving",
    "sitting": "sitting",
    "standing": "standing",
    "jumping": "jumping",
    "volleyball": "playing volleyball",
    "basketball": "playing basketball",
    "football": "playing football",
    "reading": "reading",
}

OBJECT_KEYWORDS = [
    "dog", "cat", "car", "tree", "table", "phone", "computer", "laptop",
    "ball", "volleyball", "basketball", "food", "cake", "flower", "boat",
    "bicycle", "chair", "building", "bridge", "sunset", "water", "bird"
]

def save_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower() or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    path = UPLOAD_DIR / unique_name
    path.write_bytes(content)
    return str(path)

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def infer_metadata_from_caption(caption: str) -> Dict[str, str]:
    text = normalize_text(caption)

    def first_match(mapping, default=""):
        for keyword, value in mapping.items():
            if keyword in text:
                return value
        return default

    scene = first_match(SCENE_KEYWORDS)
    weather = first_match(WEATHER_KEYWORDS)
    mood = first_match(MOOD_KEYWORDS)

    action_values = []
    for keyword, value in ACTION_KEYWORDS.items():
        if keyword in text:
            action_values.append(value)
    actions = ", ".join(dict.fromkeys(action_values))

    object_values = []
    for keyword in OBJECT_KEYWORDS:
        if keyword in text:
            object_values.append(keyword)
    objects = ", ".join(object_values)

    people = "people" if any(x in text for x in ["person", "people", "man", "woman", "boy", "girl", "child"]) else ""

    return {
        "scene": scene,
        "weather": weather,
        "people": people,
        "actions": actions,
        "objects": objects,
        "mood": mood,
    }

def vector_to_json(vector) -> str:
    if hasattr(vector, "tolist"):
        vector = vector.tolist()
    return json.dumps([float(x) for x in vector])

def json_to_vector(raw: str) -> List[float]:
    return json.loads(raw)

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def structured_score(query: str, photo) -> float:
    q = normalize_text(query)
    score = 0.0
    fields = {
        "caption": photo.caption or "",
        "scene": photo.scene or "",
        "weather": photo.weather or "",
        "people": photo.people or "",
        "actions": photo.actions or "",
        "objects": photo.objects or "",
        "mood": photo.mood or "",
    }

    for field_name, value in fields.items():
        value_n = normalize_text(value)
        if not value_n:
            continue
        if value_n in q:
            score += 0.15
        for token in value_n.split(", "):
            token = token.strip()
            if token and token in q:
                score += 0.08

    return min(score, 0.5)
