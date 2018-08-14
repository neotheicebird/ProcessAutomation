import json

with open("config.json", "rt") as fp:
    config = json.load(fp)

# configuration global variables
REGION_NAME = config["QueueRegion"]
QUEUE_URL = config["QueueURL"]
OUTPUT_FILEPATH = config["OutputFilePath"]