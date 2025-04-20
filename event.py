import pandas as pd

class Event:
    '''
    Event class to represent an event    
    '''
    def __init__(self, timestamp, translation_id, source_language, target_language, client_name, event_name, nr_words, duration):
        self.timestamp = pd.to_datetime(timestamp)
        self.translation_id = translation_id
        self.source_language = source_language
        self.target_language = target_language
        self.client_name = client_name
        self.event_name = event_name
        self.nr_words = nr_words
        self.duration = duration
    
    