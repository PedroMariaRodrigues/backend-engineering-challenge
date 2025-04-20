import json

class Writer:
    
    def __init__(self, output_destiny: str):
        self.output_destiny = output_destiny      
    
    def write(self, result: dict):
        '''
        Write the results to file or cli
        '''

        if self.output_destiny == 'cli':
            '''
            Write the result in command-line
            '''
            print(f"{json.dumps(result)}\n")
            
        else:    
            
            with open(self.output_destiny, 'a') as f_out:
                json.dump(result, f_out)
                f_out.write("\n")
        