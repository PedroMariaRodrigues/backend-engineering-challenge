from metrics_ import metrics
from datetime import datetime, timedelta
from collections import deque


def round_up_minute(dt: datetime):
    '''
    Return the timestamp up rounded to minute
    '''
    return dt.replace(second=0, microsecond=0)+timedelta(minutes=1)
    

class Processor:
    '''
    Class to process the metrics with data and time window
    '''
    
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.moving_window = deque()
        self.event_current_minute = None
        
    def popleft_moving_window(self, current_minute: datetime):
        '''
        Delete from moving window events out of the time window
        '''
        to_popleft = current_minute - timedelta(minutes=self.window_size)
        while self.moving_window and self.moving_window[0].timestamp < to_popleft:
            self.moving_window.popleft()
    
    def generate_output_for_minute(self, minute: datetime, metric):
        '''
        Generate output for a specific minute
        '''
        if metric == "moving_average":
           
            self.popleft_moving_window(minute)
            ma = metrics.moving_average(self.moving_window)
            return {"date": str(minute), "average_delivery_time": ma}
        
        ## Add other metrics
        else:
            raise ValueError(f"Unsuported metric: {metric}")
        
        
    def process(self, event, metric):
        '''
        Process events and generate outputs for every minute
        '''
                
        # Initialize the current minute if this is the first event
        if self.event_current_minute is None:
            self.event_current_minute = round_up_minute(event.timestamp)
            self.moving_window.append(event)
            return {"date": str(self.event_current_minute-timedelta(minutes=1)), "average_delivery_time": 0}
        
        # Get the minute of the current event
        event_minute = round_up_minute(event.timestamp)
        
        # If the event is in the same minute as current_minute, just add it to the window
        if event_minute == self.event_current_minute:
            self.moving_window.append(event)
            return None
            
        # The event is in a future minute, generate outputs for all minutes in between
        outputs = []
        while self.event_current_minute < event_minute:
            output = self.generate_output_for_minute(self.event_current_minute, metric)
            outputs.append(output)
            # Move to next minute
            self.event_current_minute += timedelta(minutes=1)
        
        # Add the current event to the window
        self.moving_window.append(event)
        
        # Return the outputs (could be multiple if there were gaps)
        if not outputs:
            return None
        return outputs[0] if len(outputs) == 1 else outputs
    
    def finalize(self, metric):
        '''
        Generate final output for the last minute processed
        '''
        if self.event_current_minute:
            return self.generate_output_for_minute(self.event_current_minute, metric)
        return None