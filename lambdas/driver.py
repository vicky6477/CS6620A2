import boto3
import time
import json
import urllib3

# AWS Region
AWS_REGION = "us-east-1"

# Initialize AWS clients
s3_client = boto3.client("s3", region_name=AWS_REGION)
http = urllib3.PoolManager() 

# S3 Bucket Name
BUCKET_NAME = "testbucketcs6620a2"

# External API URL 
PLOTTING_API_URL = f"https://ha3lwbtfy7.execute-api.us-east-1.amazonaws.com/a2/plot?bucket_name={BUCKET_NAME}"


def lambda_handler(event, context):
    """Creates, updates, and deletes objects in S3 to trigger S3 events."""
    try:
        print("Starting S3 operations...")

        # Step 1: Create `assignment1.txt` with the correct content
        s3_client.put_object(Bucket=BUCKET_NAME, Key="assignment1.txt", Body="Empty Assignment 1")
        print("Successfully Created assignment1.txt.")
        time.sleep(1.5)

        # Step 2: Update `assignment1.txt` with new content
        s3_client.put_object(Bucket=BUCKET_NAME, Key="assignment1.txt", Body="Empty Assignment 2222222222")
        print("Successfully updated assignment1.txt.")
        time.sleep(1.5)

        # Step 3: Delete `assignment1.txt`
        s3_client.delete_object(Bucket=BUCKET_NAME, Key="assignment1.txt")
        print("Successfully deleted assignment1.txt.")
        time.sleep(1.5)  

        # Step 4: Create `assignment2.txt` with the correct content
        s3_client.put_object(Bucket=BUCKET_NAME, Key="assignment2.txt", Body="33")
        print("Successfully created assignment2.txt.")
        time.sleep(1.5)

        # Step 5: Call the external plotting API using urllib3
        print(f"Calling plotting API: {PLOTTING_API_URL}")
        response = http.request("GET", PLOTTING_API_URL)

        response_data = json.loads(response.data.decode("utf-8"))
        print("Plotting API Response:", response_data)

        return {"statusCode": 200, "body": json.dumps(response_data)}

    except Exception as e:
        print(f"Error during Lambda execution: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Failed: {str(e)}")}
