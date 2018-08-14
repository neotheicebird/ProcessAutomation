# Generate tasks to test the process automation script
import boto3
import time
import datetime
import json
from configure import REGION_NAME, QUEUE_URL
import enlighten


if __name__ == "__main__":
    # make sure boto is configured in the same region as the queue, or else you can specify the regionname while creating the client
    # sqs_client = boto3.client("sqs", region_name='ap-south-1')
    sqs_client = boto3.client("sqs", region_name=REGION_NAME)

    print("Generating tasks")

    counter = enlighten.Counter(desc='Tasks generated', unit='tasks')
    while True:
        # generate 1 tasks every minute
        msg = json.dumps({"timestamp": datetime.datetime.today().strftime("%b %d %Y %H:%M:%S")})

        sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=msg
        )
        counter.update()
        time.sleep(.01)
