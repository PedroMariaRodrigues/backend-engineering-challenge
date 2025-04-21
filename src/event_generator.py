import random
from datetime import datetime
import time
import json
import argparse
    
def event_generator(filename, max_delay):
    '''
    Generates random events and saves them to a file
    '''
    
    while True:
    
        timer = random.randint(0, max_delay)
        duration = random.randint(1, 100)
        now = datetime.now()
        result = {"timestamp": str(now),"translation_id": "xxx","source_language": "xx","target_language": "xx","client_name": "xx","event_name": "translation_delivered","nr_words": 120,"duration": duration}
        with open(filename, 'a') as f_out:
            json.dump(result, f_out)
            f_out.write("\n")
        
        time.sleep(timer)
                    
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate random events"
    )
    
    parser.add_argument("--output_file", required=True, type = str, 
                        help = "Output file to save the generated event")
    parser.add_argument("--max_delay", default=5, type=int, 
                        help="Max delay time between generations")
    
    args = parser.parse_args()
    
    event_generator(args.output_file, args.max_delay)