import boto3
import json
import os


AWS_REGION = "us-east-1"
IAM_USER_NAME = "vickya2"
USER_PASSWORD = input("Create a strong password for the IAM user: ")

# Required IAM policies for `vickya2`
IAM_USER_POLICIES = [
    "arn:aws:iam::aws:policy/AdministratorAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
]

# Inline policy to allow `vickya2` to assume role
IAM_ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": f"arn:aws:iam::423623843212:role/a2"
        }
    ]
}

# Initialize IAM client using Root credentials
session = boto3.Session(profile_name="root")
iam_client = session.client("iam")

def create_iam_user():
    """Creates an IAM user  enables AWS Console access, and attaches necessary policies."""
    try:
        # Create the IAM user
        iam_client.create_user(UserName=IAM_USER_NAME)
        print(f"IAM User '{IAM_USER_NAME}' created successfully.")
        
        # Create login profile for the IAM user
        iam_client.create_login_profile(
            UserName=IAM_USER_NAME,
            Password=USER_PASSWORD,  
            PasswordResetRequired=True  
        )

        # Attach required policies
        for policy in IAM_USER_POLICIES:
            iam_client.attach_user_policy(UserName=IAM_USER_NAME, PolicyArn=policy)
            #print(f"Attached Policy: {policy}")

        # Attach inline assume-role policy
        iam_client.put_user_policy(
            UserName=IAM_USER_NAME,
            PolicyName="AllowAssumeRole",
            PolicyDocument=json.dumps(IAM_ASSUME_ROLE_POLICY)
        )
        
    except Exception as e:
        print(f"Error creating IAM user: {e}")

if __name__ == "__main__":
    create_iam_user()
