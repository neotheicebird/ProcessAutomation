# Looks for new tasks in SQS and processes them
import boto3
from configure import QUEUE_URL, REGION_NAME, OUTPUT_FILEPATH
import time
import json
import os


def setup():
    sqs_client = boto3.client("sqs", region_name=REGION_NAME)
    return sqs_client

def process(message_body):
    msg_dict = json.loads(message_body)

    if os.path.exists(OUTPUT_FILEPATH):
        mode = 'a'  # append if already exists
    else:
        mode = 'w'  # make a new file if not

    try:
        line = msg_dict["timestamp"] + "\n"
        with open(OUTPUT_FILEPATH, mode) as fp:
            fp.write(line)
    except KeyError:
        print("bad task. Unknown key present")


def delete_task(sqs, handle):
    # SQS messages should be explicitly deleted, just reading from queue doesn't autodelete
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=handle
    )


def notify():
    # using SNS
    pass

def get_task(sqs):
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        VisibilityTimeout=60,
        WaitTimeSeconds=2
    )

    try:
        for item in response["Messages"]:
            yield item["Body"], item["ReceiptHandle"]
    except KeyError:
        raise KeyError("Unable to read from SQS. Check your internet connection or if you have configured the project properly")


def run_task_loop(sqs):
    while True:
        for task_body, task_handle in get_task(sqs=sqs):
            process(task_body)
            delete_task(sqs, task_handle)
        else:
            # if no more tasks present, i.e a batch is completely processed, send notification
            pass

        time.sleep(0.1)
        break

def teardown():
    pass

if __name__ == "__main__":
    sqs = setup()
    run_task_loop(sqs)
