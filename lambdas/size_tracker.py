import boto3
import json
from datetime import datetime

AWS_REGION = "us-east-1"
TABLE_NAME = "S3-object-size-history"

# Initialize AWS clients
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

def get_bucket_size(bucket_name):
    """
    Calculates the total size and object count of the S3 bucket, excluding the plot image.
    Ensures that an empty bucket correctly returns (0, 0).
    """
    total_size = 0
    total_objects = 0
    paginator = s3_client.get_paginator('list_objects_v2')

    try:
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Exclude plot file from the bucket size calculation
                    if obj['Key'] == "plot":
                        continue

                    total_objects += 1
                    total_size += obj['Size']

    except Exception as e:
        print(f"Error fetching bucket size: {e}")
        return 0, 0  # Ensure that the function does not return None

    return total_size, total_objects  # Ensuring valid (size, object count) output

def lambda_handler(event, context):
    """
    AWS Lambda handler triggered by S3 events.
    Updates the DynamoDB table with the current bucket size.
    """
    try:
        print(f"Received event: {json.dumps(event)}")  # Debug log for event
        
        # Validate the event structure
        if not event.get("Records"):
            print("No records found in the event. Exiting.")
            return {"statusCode": 400, "body": json.dumps("Invalid event structure")}

        record = event["Records"][0]  
        s3_info = record.get("s3", {})
        event_name = record.get("eventName", "")

        if not s3_info:
            print("No S3 information found in the event. Exiting.")
            return {"statusCode": 400, "body": json.dumps("Invalid event structure")}
        
        bucket_name = s3_info.get("bucket", {}).get("name", "")
        if not bucket_name:
            print("No bucket name found in the event. Exiting.")
            return {"statusCode": 400, "body": json.dumps("Invalid event structure")}

        # Retrieve the current bucket size
        total_size, total_objects = get_bucket_size(bucket_name)

        # Ensure we never return None values
        if total_size is None or total_objects is None:
            total_size, total_objects = 0, 0

        # Generate a timestamp in ISO format
        timestamp = datetime.utcnow().isoformat()
        
        print(f"Updating DynamoDB: {bucket_name}, Size: {total_size}, Objects: {total_objects}")

        # Write the updated bucket size to DynamoDB
        table.put_item(Item={
            "bucket_name": bucket_name,          # Partition Key
            "timestamp": timestamp,              # Sort Key
            "total_size": int(total_size),       # Ensure integer values
            "total_objects": int(total_objects)  # Ensure integer values
        })
        
        return {"statusCode": 200, "body": json.dumps("Bucket size updated successfully")}
    
    except Exception as e:
        print(f"Error processing the event: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
