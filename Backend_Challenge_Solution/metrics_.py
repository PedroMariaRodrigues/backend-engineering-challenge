
class metrics:
    '''
    Class with the metrics available
    '''
    #Note:
    # Only need to calculate the first MA with all the data, 
    # after that can be calculated with only the new data and 
    # added to the previuos MA 
    # -> Left to implement
           
    def moving_average(events: list):
        '''
        Calculates the moving average        
        '''
        if events:
            #calculate the moving average
            delivery_time = []
            for event in events:
                delivery_time.append(event.duration)

            ma = sum(delivery_time)/len(delivery_time)
        else:
            ma = 0
        
        return ma
       
    #Add other metrics

# from collections import deque
# from read import Reader
# reader = Reader('test.json', 24*60)
# met = metrics()
# teste = reader.read_events()
# events = deque()
# for event in teste:
#     print(event.timestamp)
#     events.append(event)
#     ma = metrics.moving_average(events=events)
#     print('delivery average', ma)
