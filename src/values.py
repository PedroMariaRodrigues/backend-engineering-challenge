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
    delivery_time_op: float = Field(ge=0)

    def format_moving_average(self) -> str:
        """
        Format the event result moving average to a string
        """
        return {"date": str(self.date), "average_delivery_time": self.delivery_time_op}
    
    def format_maximum(self) -> str:
        """
        Format the event result maximum to a string
        """
        return {"date": str(self.date), "maximum": self.delivery_time_op}