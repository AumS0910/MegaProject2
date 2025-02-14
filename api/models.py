from pydantic import BaseModel
from typing import Optional, List

class BrochureRequest(BaseModel):
    hotel_name: str
    location: str
    layout: Optional[str] = "full_bleed"
    custom_prompts: Optional[dict] = None

class BrochureResponse(BaseModel):
    file_path: str
    status: str
    message: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
