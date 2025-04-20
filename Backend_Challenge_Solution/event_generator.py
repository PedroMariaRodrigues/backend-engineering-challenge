import random
from datetime import datetime
import time
import json
import argparse
    
#gerar json random com a mesma estrutura
#em tempos random para o events.json


def generator(filename, max_delay):
    
    while True:
    
        timer = random.randint(0, max_delay)
        duration = random.randint(1, 100)
        now = datetime.now()
        result = {"timestamp": str(now),"translation_id": "5aa5b2f39f7254a77664","source_language": "en","target_language": "fr","client_name": "taxi-eats","event_name": "translation_delivered","nr_words": 120,"duration": duration}
        #result = {"date": str(self.current_minute), "average_delivery_time": ma}
        with open(filename, 'a') as f_out:
            json.dump(result, f_out)
            f_out.write("\n")
        
        time.sleep(timer)
                    
                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate random events"
    )
    
    parser.add_argument("--output_file", default='events.json', type = str, 
                        help = "Output file to save the generated event")
    parser.add_argument("--max_delay", default=5, type=int, 
                        help="Max delay time between generations")
    
    args = parser.parse_args()
    
    generator(args.output_file, args.max_delay)