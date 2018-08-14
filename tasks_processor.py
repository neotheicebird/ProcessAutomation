# Looks for new tasks in SQS and processes them
import boto3
from configure import QUEUE_URL, REGION_NAME

def setup():
    sqs_client = boto3.client("sqs", region_name=REGION_NAME)
    return sqs_client

def process():
    pass

def notify():
    # using SNS
    pass

def run_task_loop(sqs):
    pass

def teardown():
    pass

if __name__ == "__main__":
    sqs = setup()
    run_task_loop(sqs)
    