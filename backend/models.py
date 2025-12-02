from pydantic import BaseModel
from typing import Dict, Any

class UpdateDocument(BaseModel):
    fields: Dict[str, Any]
