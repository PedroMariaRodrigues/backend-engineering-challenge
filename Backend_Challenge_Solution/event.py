from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    """
    Event class to represent an event using Pydantic
    """
    timestamp: datetime
    translation_id: str
    source_language: str
    target_language: str
    client_name: str
    event_name: str
    nr_words: int
    duration: float = Field(ge=0)  
