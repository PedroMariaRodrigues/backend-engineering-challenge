# Unababel Backend Engineering Challenge - Solution

This repository presents a simple command line application that parses a stream of events and produces an aggregated output. In this case, it was implemented a moving average metric. For every minute, it is calculated a moving average of the translation delivery time for the last X minutes.


## Instalation

Clone the repository

    git clone https://github.com/PedroMariaRodrigues/backend-engineering-challenge.git

    cd Backend_Challenge_Solution

Installation via setup.py

To install the application from source

    pip install .

[For editors mode use `pip install -e .`, so you don't have to be continuously reinstalling.]


## Usage

Run the CLI tool on your event data:

    unbabel_cli --input_file <INPUT_FILE> --window_size <WINDOW_SIZE> 

### Parameters

- `--input_file`: Path to the Json file containing the events
- `--window_size`: Size of the moving window in minutes
- `--metric`(Optional): Choose the metric to analyse the data 
- `--output`(Optional): Path to the output file (defaults to "output.json"), can also output to cli
- `--keep_live`(Optional): After reading all the input file, keeps reading the file in case of live update

# Project Structure
- `unbabel_cli.py`: Entry point to the application
- `event.py`: Event data model
- `metrics_.py`: Metric calculation implementations
- `process.py`: Core processing logiv for events
- `read.py`: Input handling
- `write.py`: Output Handling
- `event_generator`(Bonus): Utility to generate test event data
- `tests/`: Unit and integration tests
- `example.json`: JSON file with example of events
- `setup.py`: Configuration file for packaging the application. Defines dependencies and creates the command-line entry point.


# Event Format

```json
{
	"timestamp": "2018-12-26 18:12:19.903159",
	"translation_id": "5aa5b2f39f7254a75aa4",
	"source_language": "en",
	"target_language": "fr",
	"client_name": "airliberty",
	"event_name": "translation_delivered",
	"duration": 20,
	"nr_words": 100
}
```

# Assumptions

- Events are ordered by timestamp
- Events have the correct format
- No white lines between events


# Testing

The project includes both unit and integration tests. 

To run the tests create a new environment:

	python -m venv .venv

	.venv/Scripts/Activate.ps1

	pip install -r requirements.txt

	pytest
    
    


# Extra

You can also generate test events (random timestamp and durantion) using the event generator:


    python event_generator.py --output_file events.json --max_delay 10


## Parameters

- `--output_file`: Path to the ouptut file (the input file used for unbabel_cli)
- `--max_delay`: Maximum delay between random generated timestamp events


