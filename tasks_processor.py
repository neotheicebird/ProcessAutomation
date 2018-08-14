# Looks for new tasks in SQS and processes them
import boto3
from configure import QUEUE_URL, REGION_NAME, OUTPUT_FILEPATH, SNS_TOPIC_ARN, SNS_TOPIC_REGION
import time
import json
import os


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
    print("NOTIFYING")
    message = "Complete"
    # using SNS
    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
    )
    # print(response)


def get_tasks(sqs):
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        VisibilityTimeout=60,
        WaitTimeSeconds=1
    )

    # print(response)

    try:
        for item in response["Messages"]:
            yield item["Body"], item["ReceiptHandle"]
    except KeyError:
        return None
        # raise KeyError("Unable to read from SQS. Check your internet connection or if you have configured the project properly")


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
    sqs, sns = setup()
    run_task_loop(sqs, sns)
