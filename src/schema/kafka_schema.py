from typing import Dict, Any
from pydantic import BaseModel

class ArxivToCrossrefMessage(BaseModel):
    author: str = ''
    title: str = ''
    start_date: str = ''
    arxiv_doi: str
    arxiv_version: int

class DlqMessage(BaseModel):
    original_message: Dict[str, Any]
    error_type: str
    error_details: str
    timestamp: str

