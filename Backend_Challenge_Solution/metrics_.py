
class metrics:
    '''
    Class with the available metrics
    '''
    #Note:
    # For cases with a huge amount of data:
    # Only need to calculate the first MA with all the data, 
    # after that it can be calculated adding the new data and removing data out of the time window 
    # and add the previous MA calculated
           
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