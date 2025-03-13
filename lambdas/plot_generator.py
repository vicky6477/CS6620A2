import sys
sys.path.append("/opt/python")  # Ensure Lambda Layer dependencies are included

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for AWS Lambda

import matplotlib.pyplot as plt
import boto3
import io
import json
from datetime import datetime, timedelta

AWS_REGION = "us-east-1"
BUCKET_NAME = "testbucketcs6620a2"  # The assignment specifies TestBucket

# Initialize AWS clients
s3_client = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table("S3-object-size-history")

def fetch_bucket_size_data():
    """Fetches the bucket size data for TestBucket from DynamoDB for the last 15 seconds."""
    try:
        now = datetime.utcnow()
        ten_seconds_ago = now - timedelta(seconds=15)

        print(f"Querying last 15 seconds of data for bucket: {BUCKET_NAME}")
        
        # Query DynamoDB for the last 15 seconds of TestBucket
        response = table.query(
            KeyConditionExpression="bucket_name = :b AND #ts BETWEEN :t_start AND :t_now",
            ExpressionAttributeNames={"#ts": "timestamp"},
            ExpressionAttributeValues={
                ":b": BUCKET_NAME,
                ":t_start": ten_seconds_ago.isoformat(),
                ":t_now": now.isoformat()
            },
            ScanIndexForward=True  # Ascending order
        )

        timestamps = [datetime.fromisoformat(item["timestamp"]) for item in response.get("Items", [])]
        sizes = [int(item["total_size"]) for item in response.get("Items", [])]

        # Find the historical maximum bucket size for TestBucket
        max_size_response = table.query(
            KeyConditionExpression="bucket_name = :b",
            ExpressionAttributeValues={":b": BUCKET_NAME},
            ProjectionExpression="total_size"
        )

        all_sizes = [int(item["total_size"]) for item in max_size_response.get("Items", [])]
        historical_max = max(all_sizes) if all_sizes else 0

        return timestamps, sizes, historical_max

    except Exception as e:
        print(f"Error fetching data from DynamoDB: {e}")
        return [], [], 0

def generate_plot():
    """Generates a plot of the bucket size over time and returns it as a buffer."""
    timestamps, sizes, historical_max = fetch_bucket_size_data()

    plt.figure(figsize=(6, 4))
    
    if timestamps:
        plt.plot(timestamps, sizes, marker="o", linestyle="-", label="Bucket Size")
        plt.axhline(y=historical_max, color="r", linestyle="--", label="Max Size Ever")
    else:
        plt.text(0.5, 0.5, "No data available for the last 15 seconds", ha='center', va='center', transform=plt.gca().transAxes)

    plt.xlabel("Time")
    plt.ylabel("Size (bytes)")
    plt.xticks(rotation=45)
    plt.title(f"S3 Bucket Size Over Time: {BUCKET_NAME}")
    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    
    return buffer

def upload_plot(image_buffer):
    """Uploads the generated plot to S3."""
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key="plot",  # The assignment specifies this should be named 'plot'
            Body=image_buffer,
            ContentType="image/png",
            ContentDisposition="inline; filename=plot.png"
        )
        print(f"Plot successfully uploaded to S3: s3://{BUCKET_NAME}/plot")
        return {"statusCode": 200, "body": json.dumps(f"Plot uploaded successfully to {BUCKET_NAME}")}

    except Exception as e:
        print(f"Failed to upload plot to S3: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Failed to upload plot: {str(e)}")}

def lambda_handler(event, context):
    """AWS Lambda function triggered by API Gateway request."""
    try:
        print(f"Received event: {json.dumps(event)}")  # Log for debugging

        # Generate and upload the plot
        image_buffer = generate_plot()
        return upload_plot(image_buffer)

    except Exception as e:
        print(f"Error processing request: {e}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
