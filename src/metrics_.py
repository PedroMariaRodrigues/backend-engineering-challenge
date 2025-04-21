available_metrics = {
    "moving_average": MovingAverage,
    "maximum": Maximum
}
class Metrics:
    '''
    Class with the available metrics
    '''
    def compute() -> int:
        pass
    

class MovingAverage(Metrics):
    '''
    Calculates the moving average of the events
    '''
    #Note:
    # For cases with a huge amount of data:
    # Only need to calculate the first MA with all the data, 
    # after that it can be calculated adding the new data and removing data out of the time window 
    # and add the previous MA calculated
        
    def compute(self, events: list) -> float:
        # Check if events is empty
        if not events:
            return 0
        
        # Calculate the moving average
        delivery_time = []
        for event in events:
            delivery_time.append(event.duration)
        
        ma = sum(delivery_time) / len(delivery_time)
        return ma
       
#Add other metrics
class Maximum(Metrics):
    '''
    Calculates the maximum of the events
    '''
    
    def compute(self, events: list) -> float:
        
        # Check if events is empty
        if not events:
            return 0
        
        # Calculate the maximum
        delivery_time = []
        for event in events:
            delivery_time.append(event.duration)
        
        max_value = max(delivery_time)
        return max_value