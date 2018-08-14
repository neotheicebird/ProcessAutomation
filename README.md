# ProcessAutomation
A lightweight orchestration framework to automate local tasks on AWS

When installed on a worker instance, this project can be used to read
through a task queue, assign and complete the tasks until the queue is emptyy.

Once the queue gets empty a notification is sent and the task_loop waits for more
tasks to pop up.

# Setup Instructions

## Setting up the project

1. Open a terminal session and clone the Githbu repo into a local directory

```
git clone https://github.com/neotheicebird/ProcessAutomation.git
```

2. Create and activate a python virtual environment for the project

```
virtualenv -p /path/to/python3 processAutomationEnv
source processAutomationEnv/bin/activate
```

3. Install required libraries to run the project

```
pip install -r requirements.txt
```

If you are a developer, you can install the `requirements-dev.txt` instead.

4. Configure boto

A) For boto to work in any local machine, we need to enable programmatic access to your AWS account from that machine

Before you can begin using Boto 3, you should set up authentication credentials. Credentials for your AWS account can be found in the IAM Console. You can create or use an existing user. Go to manage access keys and generate a new set of keys.

I created an IAM user named `process_automator` and attach existing policies directly to the user: `AmazonSNSFullAccess, AmazonSQSFullAccess, AmazonEC2FullAccess` 

(You can also attach `AdministratorAccess` while you are developing or for testing. But this must be removed later.)

Check programmatic access to the user and downloaded the `aws_key` and `aws_secret` for the user.

If you have the AWS CLI installed, then you can use it to configure your credentials file:

`aws configure`

Alternatively, you can create the credential file yourself. By default, its location is at ~/.aws/credentials:

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```
You may also want to set a default region. This can be done in the configuration file. By default, its location is at ~/.aws/config:

```
[default]
region=us-east-1
```
Alternatively, you can pass a region_name when creating clients and resources.

Ref: https://boto3.readthedocs.io/en/latest/guide/quickstart.html#installation

# How to use the program?

On your server, run `tasks_processor.py`

```
python tasks_processor.py
```

For testing, you can generate tasks at 1task/sec using `task_generator.py`

What I do is, while `tasks_processor.py` is active, I run `task_generator.py` for a 
few seconds and then kill (Ctrl+C), instantly you should see an SNS notification sent as queue is now empty.

# Future work

1. Assigning tasks to process() is now done serially, which can be updated to a concurrency model
This may not be required if this automation script is spawned across multiple workers.

2. A master script to orchestrate spawning of multiple worker instances and setup this automation script needs to be done.




