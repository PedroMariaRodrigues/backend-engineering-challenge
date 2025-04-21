import argparse
import sys
import os
from read import Reader
from process import Processor
from write import Writer       

def main():
    '''
    Function to orchestrate the processing of events
    '''
    
    parser = argparse.ArgumentParser(description="Process data from the last X minutes")
    
    parser.add_argument("--input_file", type=str, required=True, 
                        help="Input file to process")
    parser.add_argument("--window_size", type=int, required=True, 
                        help='Window size to process data in minutes')
    parser.add_argument("--metric", type=str, default="moving_average", choices=["moving_average", "maximum"], 
                        help="""Available metrics:\n
                        - moving_average(default) -> Moving average of the last x minutes\n
                        - maximum -> Maximum of the last x minutes""")
    parser.add_argument("--output", type=str, default="output.json",
                        help = """The results can be outputed to:
                        -file (default) -> Add the destiny desired file and format
                        -cli  -> Output the results to the terminal""")
    parser.add_argument("--keep_live", action='store_true', 
                        help= "After analyze the all input file, keep waiting to read live")
     
    args = parser.parse_args() 
    
    #Validate input file
    if not os.path.isfile(args.input_file):
        raise FileNotFoundError(f"The file '{args.input_file}' does not exist.")

    #Validate window size
    if args.window_size <= 0:
        raise ValueError("The window size must be a positive integer.")

            
    reader = Reader(args.input_file, args.keep_live)
    processor = Processor(args.window_size, args.metric)
    writer = Writer(args.output)
   
    try:
    # First process all existing events
        for event in reader.read_existing_events():
            result = processor.process(event)

            # Handle single result
            if result and isinstance(result, dict):
                writer.write(result)

            # Handle multiple results (gap filling)
            elif result and isinstance(result, list):
                for r in result:
                    writer.write(r)

        if not args.keep_live:
            # Process the final minute of existing events, 
            # if live wait for possible events in the same minute
            final_result = processor.finalize()
            if final_result:
                writer.write(final_result)

        # Now start monitoring for live events if requested
        if args.keep_live:
            print("Processing complete. Monitoring for new events...")
            for event in reader.monitor_live_events():
                result = processor.process(event)
                if result:
                    if isinstance(result, dict):
                        writer.write(result)
                    else:
                        for r in result:
                            writer.write(r)

    except KeyboardInterrupt:
        #If keyboard interrupt is detected, calculate the last minute
        final_result = processor.finalize()
        if final_result:
            writer.write(final_result)
        print("Terminating Successfully")
        sys.exit(0)
       
    
if __name__ == "__main__":
    main()