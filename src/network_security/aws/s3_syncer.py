import boto3
import os
from dotenv import load_dotenv

from network_security.utils.logger import logging

load_dotenv()

# AWS Credentials
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
REGION = os.getenv("AWS_REGION")

# Initialize S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def list_s3_files(bucket_name=BUCKET_NAME, prefix=""):
    """
    Get a list of all files in an S3 bucket under a specific prefix.

    Args:
        bucket_name (str): Name of the S3 bucket.
        prefix (str): Prefix to filter files.

    Returns:
        dict: Dictionary of file paths and their sizes in the bucket.
    """
    s3_files = {}
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                s3_files[obj['Key']] = obj['Size']
    return s3_files

def upload_folder_to_s3(folder_path, skip_if_exists=True, bucket_name=BUCKET_NAME, s3_prefix=""):
    """
    Upload all files from a local folder to an S3 bucket, skipping already uploaded files.

    Args:
        folder_path (str): Local folder path to sync.
        bucket_name (str): S3 bucket name.
        s3_prefix (str): Prefix for files in the bucket.
    """
    existing_files = list_s3_files(bucket_name, s3_prefix)

    for root, _, files in os.walk(folder_path):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, folder_path)
            s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")  # Ensure S3 path uses '/'

            # Skip if file already exists and sizes match
            if skip_if_exists and s3_path in existing_files and os.path.getsize(local_path) == existing_files[s3_path]:
                logging.info(f"Skipping {local_path}, already exists in S3.")
                continue

            try:
                logging.info(f"Uploading {local_path} to s3://{bucket_name}/{s3_path}...")
                s3_client.upload_file(local_path, bucket_name, s3_path)
                logging.info(f"Uploaded {local_path} successfully.")
            except Exception as e:
                logging.info(f"Failed to upload {local_path}: {str(e)}")

def download_s3_to_local(s3_prefix, local_folder, bucket_name=BUCKET_NAME):
    """
    Download files from S3 to the local folder if they don't already exist locally.

    Args:
        s3_prefix (str): Prefix for files in the bucket.
        local_folder (str): Local folder to sync files.
        bucket_name (str): S3 bucket name.
    """
    s3_files = list_s3_files(bucket_name, s3_prefix)

    for s3_path, size in s3_files.items():
        relative_path = os.path.relpath(s3_path, s3_prefix)
        local_path = os.path.join(local_folder, relative_path)

        # Skip if file already exists and sizes match
        if os.path.exists(local_path) and os.path.getsize(local_path) == size:
            logging.info(f"Skipping {s3_path}, already exists locally.")
            continue

        # Create local directories if needed
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        try:
            logging.info(f"Downloading s3://{bucket_name}/{s3_path} to {local_path}...")
            s3_client.download_file(bucket_name, s3_path, local_path)
            logging.info(f"Downloaded {s3_path} successfully.")
        except Exception as e:
            logging.info(f"Failed to download {s3_path}: {str(e)}")

# # Define folders and S3 prefixes
# folders_to_sync = {
#     "final_model": "final_model_prefix",
#     "artifacts": "artifacts_prefix"
# }

# # Sync each folder
# for local_folder, s3_prefix in folders_to_sync.items():
#     logging.info(f"Syncing {local_folder} with s3://{BUCKET_NAME}/{s3_prefix}...")
#     upload_folder_to_s3(local_folder, BUCKET_NAME, s3_prefix)  # Upload from local to S3
#     download_s3_to_local(BUCKET_NAME, s3_prefix, local_folder)  # Download from S3 to local
