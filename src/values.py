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
    
class EventResult(BaseModel):
    """
    EventResult class to represent the result aggregated events
    """
    date: datetime
    average_delivery_time: float = Field(ge=0)

    def format(self) -> str:
        """
        Format the event to a string
        """
        return {"date": str(self.date), "average_delivery_time": self.average_delivery_time}