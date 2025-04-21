from metrics_ import Metrics, MovingAverage, Maximum
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional, Any, Deque
from collections import deque
from values import Event, EventResult
from metrics_ import available_metrics


def round_up_minute(dt: datetime) -> datetime:
    '''
    Return the timestamp up rounded to minute
    '''
    return dt.replace(second=0, microsecond=0)+timedelta(minutes=1)
    

class Processor:
    '''
    Class to process the metrics with data and time window
    '''
    
    def __init__(self, window_size: int, metric:str = "moving_average") -> None:
        self.window_size: int = window_size
        self.moving_window: Deque[Event] = deque()
        self.event_current_minute: Optional[datetime] = None
        self.metric: Metrics = self.get_metrics(metric)
        self.supported_metrics = available_metrics.keys()
        
    def get_metrics(self, metric: str) -> Metrics:
        if metric == "moving_average":
            return MovingAverage()
        elif metric == "maximum":
            return Maximum()
        
        
    def popleft_moving_window(self, current_minute: datetime) -> None:
        '''
        Delete from moving window events out of the time window
        '''
        to_popleft: datetime = current_minute - timedelta(minutes=self.window_size)
        while self.moving_window and self.moving_window[0].timestamp < to_popleft:
            self.moving_window.popleft()
    
    def generate_output_for_minute(self, minute: datetime, metric: str) -> Dict[str, Any]:
        '''
        Generate output for a specific minute
        '''
                 
        self.popleft_moving_window(minute)
        result = self.metric.compute(self.moving_window)
        event_result = EventResult(date=minute, delivery_time_op=result)
        return event_result.format_moving_average() if metric == "moving_average" else event_result.format_maximum()
        
        
    def process(self, event: Event, metric: str) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        '''
        Process events and generate outputs for every minute
        '''
        # Check if the metric is supported
        if metric not in self.supported_metrics:
            raise ValueError("Unsuported metric")
                
        # Initialize the current minute if this is the first event
        if self.event_current_minute is None:
            self.event_current_minute = round_up_minute(event.timestamp)
            self.moving_window.append(event)
            event_result = EventResult(date=self.event_current_minute-timedelta(minutes=1), delivery_time_op=0)
            return event_result.format_moving_average() if metric == "moving_average" else event_result.format_maximum()
        
        # Get the minute of the current event
        event_minute = round_up_minute(event.timestamp)
        
        # If the event is in the same minute as current_minute, just add it to the window
        if event_minute == self.event_current_minute:
            self.moving_window.append(event)
            return None
            
        # The event is in a future minute, generate outputs for all minutes in between
        outputs: List[Dict[str, Any]] = []
        while self.event_current_minute < event_minute:
            output: Dict[str, Any] = self.generate_output_for_minute(self.event_current_minute, metric)
            outputs.append(output)
            # Move to next minute
            self.event_current_minute += timedelta(minutes=1)
        
        # Add the current event to the window
        self.moving_window.append(event)
        
        # Return the outputs (could be multiple if there were gaps)
        if not outputs:
            return None
        return outputs[0] if len(outputs) == 1 else outputs
    
    def finalize(self, metric) -> Optional[Dict[str, Any]]:
        '''
        Generate final output for the last minute processed
        '''
        if self.event_current_minute:
            return self.generate_output_for_minute(self.event_current_minute, metric)
        return None