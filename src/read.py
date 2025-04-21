import json
import sys
import os
import time
from typing import Generator
from values import Event

class Reader:
    '''
    Class to read the events from the file
    '''
    
    def __init__(self, filename: str, keep_reading_live: bool) -> None:
        self.filename = filename  
        self.keep_reading_live = keep_reading_live  
        self.last_position = 0  
         
    def parse_event(self, line: str) -> Event:
        '''
        Parse the event from the line
        '''
        # Parse JSON line
        try:
            event_data = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
           
        try:
            
            event = Event(
                timestamp = event_data['timestamp'],
                translation_id = event_data['translation_id'],
                source_language = event_data['source_language'],
                target_language = event_data['target_language'],
                client_name = event_data['client_name'],
                event_name = event_data['event_name'],
                nr_words = event_data['nr_words'],
                duration = event_data['duration']
            )
        
            return event
        except KeyError as e:
            raise ValueError(f"Missing key in JSON data: {e}")                
    
    def read_existing_events(self) -> Generator[Event, None, None]:
        """
        Read only events that already exist in the file.
        """
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    try:
                        event = self.parse_event(line)
                        yield event
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {line}")
                    except KeyError as e:
                        print(f"Missing required key in event: {e}")
            
            # Store the current file position for live monitoring
            if self.keep_reading_live:
                self.last_position = os.path.getsize(self.filename)
        
        except FileNotFoundError:
            print(f"File not found: {self.filename}")
            sys.exit(1)
    
    def monitor_live_events(self) -> Generator[Event, None, None]:
        """
        Monitor the file for new events after reading existing ones.
        """
        if not self.keep_reading_live:
            return

        try:
            while True:
                try:
                    with open(self.filename, 'r') as file:
                        file.seek(self.last_position)

                        line = file.readline()
                        if line:
                            line = line.strip()
                            if not line:  # Skip empty lines
                                continue

                            try:
                                event = self.parse_event(line)
                                # Update position before yielding
                                self.last_position = file.tell()
                                yield event
                            except json.JSONDecodeError:
                                print(f"Error decoding JSON: {line}")
                                self.last_position = file.tell()  # Skip bad JSON
                            except KeyError as e:
                                print(f"Missing required key in event: {e}")
                                self.last_position = file.tell()  # Skip bad event
                        else:
                            # No new line, pause before retrying
                            time.sleep(0.5)
                except FileNotFoundError:
                    print(f"File not found: {self.filename}")
                    time.sleep(1)  # Wait and retry if file monitoring

        except Exception as e:
            print(f"Error monitoring file: {e}")
            sys.exit(1)