# Looks for new tasks in SQS and processes them
import boto3
from configure import QUEUE_URL, REGION_NAME, OUTPUT_FILEPATH, SNS_TOPIC_ARN, SNS_TOPIC_REGION
import time
import json
import os
import logging
import botocore

# basic logging setup
logger = logging.getLogger("tasks_processor")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('errors.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)



def setup():
    sqs_client = boto3.client("sqs", region_name=REGION_NAME)
    sns_client = boto3.client("sns", region_name=SNS_TOPIC_REGION)

    return sqs_client, sns_client

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
        raise KeyError("bad task. Unknown key present")


def delete_task(sqs, handle):
    # SQS messages should be explicitly deleted, just reading from queue doesn't autodelete
    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=handle
    )


def notify(sns):
    print("Publishing `Complete`")
    message = "Complete"

    # using SNS
    try:
        response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        )
    except botocore.exceptions.EndpointConnectionError:
        logger.info("Unable to connect to AWS. SNS publish failed")
        raise


def get_tasks(sqs):
    try:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=10,
            VisibilityTimeout=60,
            WaitTimeSeconds=1
        )
    except botocore.exceptions.EndpointConnectionError:
        logger.info("Unable to connect to AWS. SQS receive messages failed")
        raise

    try:
        for item in response["Messages"]:
            yield item["Body"], item["ReceiptHandle"]
    except KeyError:
        return None


def run_task_loop(sqs, sns):
    notified = False

    while True:
        found_msgs = False  # flag to check if any msgs were read in an attempt
        for task_body, task_handle in get_tasks(sqs=sqs):
            process(task_body)
            delete_task(sqs, task_handle)
            found_msgs = True
            notified = False

        if not found_msgs and not notified:
            # if no more tasks present, i.e a batch is completely processed, send notification
            notify(sns=sns)
            notified = True

        time.sleep(0.1)


if __name__ == "__main__":
    print("Starting automation")
    sqs, sns = setup()
    run_task_loop(sqs, sns)
