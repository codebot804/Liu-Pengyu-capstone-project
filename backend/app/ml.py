from __future__ import annotations
import os
from functools import lru_cache
from typing import Dict, List

import numpy as np
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor, CLIPModel, CLIPProcessor

from .utils import infer_metadata_from_caption

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class MLLMService:
    def __init__(self):
        self._caption_processor = None
        self._caption_model = None
        self._clip_processor = None
        self._clip_model = None

    def _load_caption_model(self):
        if self._caption_processor is None or self._caption_model is None:
            self._caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self._caption_model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            ).to(DEVICE)
        return self._caption_processor, self._caption_model

    def _load_clip_model(self):
        if self._clip_processor is None or self._clip_model is None:
            self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE)
        return self._clip_processor, self._clip_model

    def caption_image(self, image_path: str) -> str:
        processor, model = self._load_caption_model()
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        output = model.generate(**inputs, max_new_tokens=40)
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption.strip()

    def image_embedding(self, image_path: str) -> List[float]:
        processor, model = self._load_clip_model()
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            feats = model.get_image_features(**inputs)
        feats = feats / feats.norm(dim=-1, keepdim=True)
        return feats[0].detach().cpu().numpy().astype(float).tolist()

    def text_embedding(self, text: str) -> List[float]:
        processor, model = self._load_clip_model()
        inputs = processor(text=[text], return_tensors="pt", padding=True).to(DEVICE)
        with torch.no_grad():
            feats = model.get_text_features(**inputs)
        feats = feats / feats.norm(dim=-1, keepdim=True)
        return feats[0].detach().cpu().numpy().astype(float).tolist()

    def analyze(self, image_path: str) -> Dict[str, object]:
        caption = self.caption_image(image_path)
        embedding = self.image_embedding(image_path)
        metadata = infer_metadata_from_caption(caption)
        return {
            "caption": caption,
            "embedding": embedding,
            **metadata,
        }

@lru_cache(maxsize=1)
def get_mllm_service() -> MLLMService:
    return MLLMService()
