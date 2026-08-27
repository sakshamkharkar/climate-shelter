from pydantic import BaseModel
from typing import Optional, Dict, Any

class ReportGenerateRequest(BaseModel):
    location_name: str = "Leh, Ladakh"
    latitude: float = 34.1526
    longitude: float = 77.5771

class ReportGenerateResponse(BaseModel):
    report_title: str
    content_markdown: str
    timestamp: str
    metadata: Dict[str, Any]
