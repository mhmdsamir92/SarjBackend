from pydantic import BaseModel
from typing import List

class SummaryRecipe(BaseModel):
    author: str
    language: str
    summary: str
    sentiment: str
    key_characters: List[str]
