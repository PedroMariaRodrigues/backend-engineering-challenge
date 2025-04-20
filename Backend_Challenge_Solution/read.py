import json
import sys
import os
import time
from datetime import datetime
from event import Event

class Reader:
    
    def __init__(self, filename: str, keep_reading_live: bool):
        self.filename = filename  
        self.keep_reading_live = keep_reading_live  
        self.filepath = filename
        self.last_position = 0
        self.file = None  
         
    def parse_event(self, line: str):
        '''
        Parse the event from the line
        '''
        # Parse JSON line
        try:
             # Parse line with JSON data
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

    
    # def read_events(self):
    #     """
    #     Read events from file, yielding one event at a time
    #     Stops at EOF unless keep_reading_live is True
    #     """
    #     pointer = 0

    #     while True:  
              
    #         with open(self.filename, 'r') as file:
                    
    #             #Jump to the last read postition
    #             file.seek(pointer)
    #             line = file.readline()

    #             if not line:
    #                 #EOF reached
    #                 if self.keep_reading_live is True:
    #                     time.sleep(1)
    #                     continue
    #                 else:
    #                     #print('Finished analysing the file.')
    #                     return

    #             pointer = file.tell()
    #             event = self.parse_event(line)

    #             yield event
                
    
    def read_existing_events(self):
        """Read only events that already exist in the file."""
        try:
            with open(self.filepath, 'r') as f:
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
                self.last_position = os.path.getsize(self.filepath)
        
        except FileNotFoundError:
            print(f"File not found: {self.filepath}")
            sys.exit(1)
    
    def monitor_live_events(self):
        """Monitor the file for new events after reading existing ones."""
        if not self.keep_reading_live:
            return
            
        try:
            self.file = open(self.filepath, 'r')
            # Move to the last read position
            self.file.seek(self.last_position)
            
            while True:
                line = self.file.readline()
                if line:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                        
                    try:
                        event = self.parse_event(line)
                        # Update the position for next read
                        self.last_position = self.file.tell()
                        yield event
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {line}")
                    except KeyError as e:
                        print(f"Missing required key in event: {e}")
                else:
                    # No new line, wait before trying again
                    time.sleep(0.1)  # Add small delay to reduce CPU usage
                    
        except FileNotFoundError:
            print(f"File not found: {self.filepath}")
            sys.exit(1)
        finally:
            if self.file:
                self.file.close()

# reader = Reader('test.json', keep_reading_live=False)
# for i, event in enumerate(reader.read_events()):
    
#     print(i, event.timestamp, event.duration)