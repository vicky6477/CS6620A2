import boto3
import os

AWS_REGION = "us-east-1"
AWS_OUTPUT_FORMAT = "json"  
def list_roles():
    """Fetch all IAM roles and let the user select one."""
    try:
        session = boto3.Session(profile_name="vickya2")
        iam_client = session.client("iam")

        response = iam_client.list_roles()
        roles = response.get("Roles", [])

        if not roles:
            print("No IAM roles found. Ensure you have created a role before running this script.")
            return None

        print("\nAvailable IAM Roles:")
        for idx, role in enumerate(roles):
            print(f"{idx + 1}. {role['RoleName']} ({role['Arn']})")

        # Allow user to select a role
        while True:
            choice = input("Enter the number of the IAM role you want to use: ")
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(roles):
                    selected_role = roles[choice]
                    print(f"Selected IAM Role: {selected_role['RoleName']} (ARN: {selected_role['Arn']})")
                    return selected_role["Arn"]
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    except Exception as e:
        print(f"Failed to fetch IAM roles: {e}")
        return None

def assume_role():
    """Assume the selected IAM role and return temporary credentials."""
    try:
        role_arn = list_roles()
        if not role_arn:
            print("Exiting... No IAM role selected.")
            exit(1)

        session = boto3.Session(profile_name="vickya2") 
        sts_client = session.client("sts")

        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession"
        )

        credentials = assumed_role["Credentials"]
        return {
            "aws_access_key_id": credentials["AccessKeyId"],
            "aws_secret_access_key": credentials["SecretAccessKey"],
            "aws_session_token": credentials["SessionToken"]
        }

    except Exception as e:
        print(f"Failed to assume IAM role: {e}")
        return None

# Get temporary credentials for the selected IAM role
temp_credentials = assume_role()
if not temp_credentials:
    print("Exiting... IAM role assumption failed.")
    exit(1)

# Initialize AWS session with assumed role credentials
session = boto3.Session(
    aws_access_key_id=temp_credentials["aws_access_key_id"],
    aws_secret_access_key=temp_credentials["aws_secret_access_key"],
    aws_session_token=temp_credentials["aws_session_token"],
    region_name=AWS_REGION
)

s3_client = session.client("s3")

BUCKET_NAME = "testbucketcs6620a2"
TABLE_NAME = "S3-object-size-history"

def create_s3_bucket():
    """Creates an S3 bucket using the assumed IAM role. Checks if it already exists before creating."""
    try:
        # Check if bucket already exists
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"S3 Bucket '{BUCKET_NAME}' already exists.")
    except s3_client.exceptions.ClientError:
        try:
            if AWS_REGION == "us-east-1":
                s3_client.create_bucket(Bucket=BUCKET_NAME)
            else:
                s3_client.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
                )
            print(f"S3 Bucket '{BUCKET_NAME}' created successfully.")
        except Exception as e:
            print(f"Failed to create S3 bucket: {e}")

def create_dynamodb_table():
    """Creates a DynamoDB table if it does not already exist."""
    try:
        # Check if table already exists
        dynamodb_client = session.client("dynamodb")
        existing_tables = dynamodb_client.list_tables()["TableNames"]

        if TABLE_NAME in existing_tables:
            print(f"DynamoDB table '{TABLE_NAME}' already exists.")
            return

        # Create DynamoDB table
        dynamodb_resource = session.resource("dynamodb")
        table = dynamodb_resource.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "bucket_name", "KeyType": "HASH"},  # Partition Key
                {"AttributeName": "timestamp", "KeyType": "RANGE"}  # Sort Key
            ],
            AttributeDefinitions=[
                {"AttributeName": "bucket_name", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        print(f"DynamoDB table '{TABLE_NAME}' created successfully.")

    except Exception as e:
        print(f"Failed to create DynamoDB table: {e}")

if __name__ == "__main__":
    create_s3_bucket()
    create_dynamodb_table()
