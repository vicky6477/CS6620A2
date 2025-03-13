import boto3
import json
import os

AWS_REGION = "us-east-1"
IAM_ROLE_NAME = "a2"
IAM_USER_NAME = "vickya2"

# Policies required for a2
IAM_ROLE_POLICIES = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
]

# Trust policy for IAM role a2
TRUST_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": f"arn:aws:iam::423623843212:user/{IAM_USER_NAME}"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
 # Policy to allow publishing Lambda layers
LAYER_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaLayerPublishing",
            "Effect": "Allow",
            "Action": "lambda:PublishLayerVersion",
            "Resource": "*"
        }
    ]
}




# Initialize IAM client using vickya2 profile
session = boto3.Session(profile_name=IAM_USER_NAME)
iam_client = session.client("iam")

def create_iam_role():
    """Creates an IAM role and attaches required policies."""
    try:
        response = iam_client.create_role(
            RoleName=IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(TRUST_POLICY)
        )
        role_arn = response["Role"]["Arn"]
        print(f"Created IAM Role: {IAM_ROLE_NAME }")

        # Attach required policies to IAM role
        for policy in IAM_ROLE_POLICIES:
            iam_client.attach_role_policy(RoleName=IAM_ROLE_NAME, PolicyArn=policy)
            #print(f"Attached Policy: {policy}")

        return role_arn

    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"IAM Role '{IAM_ROLE_NAME}' already exists. Fetching ARN...")
        response = iam_client.get_role(RoleName=IAM_ROLE_NAME)
        return response["Role"]["Arn"]

    except Exception as e:
        print(f"Error creating IAM Role: {e}")
        return None

if __name__ == "__main__":
    role_arn = create_iam_role()
    #print(f"Role setup complete. IAM Role ARN: {role_arn}")