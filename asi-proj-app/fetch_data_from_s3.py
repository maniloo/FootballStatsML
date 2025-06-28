import boto3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
AWS_REGION = "eu-central-1"

def fetch_everything(destination_path: str) -> None:
    """Fetch all files from S3 bucket and save to provided local path, including database catalog. Skip if folder is not empty."""
    import os
    bucket_name = "my-football-models"
    s3_prefixes = ["models/", "database/"]
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    local_path = Path(destination_path).resolve()
    # Skip operation if folder is not empty
    if local_path.exists() and any(local_path.iterdir()):
        logger.info(f"🚫 Skipping fetch: {local_path} is not empty.")
        return None
    total_file_count = 0
    for s3_prefix in s3_prefixes:
        logger.info(f"⬇️ Fetching all from s3://{bucket_name}/{s3_prefix} to {local_path}")
        file_count = 0
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
            if 'Contents' not in response:
                logger.warning(f"No files found in s3://{bucket_name}/{s3_prefix}")
                continue
            for obj in response['Contents']:
                s3_key = obj['Key']
                if s3_key.endswith('/'):
                    continue  # skip folders
                rel_path = s3_key[len(s3_prefix):]
                target_file = local_path / s3_prefix.strip('/') / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    s3_client.download_file(bucket_name, s3_key, str(target_file))
                    file_count += 1
                    if file_count % 50 == 0:
                        logger.info(f"⬇️ {file_count} files downloaded from {s3_prefix}...")
                except Exception as e:
                    logger.error(f"❌ Failed to download {s3_key}: {e}")
            logger.info(f"✅ Downloaded {file_count} files from s3://{bucket_name}/{s3_prefix}")
            total_file_count += file_count
        except Exception as e:
            logger.error(f"❌ Error fetching from {s3_prefix}: {e}")
    logger.info(f"⬇️ Total files downloaded: {total_file_count}")

    return None
