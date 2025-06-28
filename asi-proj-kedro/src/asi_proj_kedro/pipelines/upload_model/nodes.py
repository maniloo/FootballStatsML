"""
This is a boilerplate pipeline 'upload_model'
generated using Kedro 0.19.12
"""

import pandas as pd
from autogluon.tabular import TabularPredictor
import boto3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
AWS_REGION = "eu-central-1"


def upload_everything(_input: TabularPredictor) -> pd.DataFrame:
    """Upload całego katalogu do S3"""

    bucket_name = "my-football-models"
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    models_dir = './../../data/08_reporting/'
    local_path = Path(models_dir).resolve()

    logger.info(f"🚀 Wysyłam wszystko z {local_path} do s3://{bucket_name}/")

    file_count = 0

    # Sprawdź, czy katalog istnieje
    # if not local_path.exists() or not local_path.is_dir():
    #     logger.error(f"❌ Katalog {local_path} nie istnieje lub nie jest katalogiem.")
    #     return pd.DataFrame({"status": ["error"], "message": ["Directory does not exist or is not a directory"]})
    # for file_path in local_path.rglob("*"):
    #     if file_path.is_file():
    #         # Użyj relatywnej ścieżki jako klucz S3
    #         model_key = str(file_path.relative_to(local_path)).replace("\\", "/")
    #         s3_key = f"models/{model_key}"
    #
    #         try:
    #             s3_client.upload_file(str(file_path), bucket_name, s3_key)
    #             file_count += 1
    #
    #             if file_count % 50 == 0:
    #                 logger.info(f"📤 {file_count} plików...")
    #
    #         except Exception as e:
    #             logger.error(f"❌ Błąd: {file_path} -> {e}")
    #             continue

    logger.info(f"✅ Wysłano {file_count} plików do s3://{bucket_name}/models/")

    try:
        additional_file = Path("./../../data/05_final_data/goals_features_data.csv")
        if additional_file.exists():
            s3_key = f"database/{additional_file.name}"
            s3_client.upload_file(str(additional_file), bucket_name, s3_key)
            file_count += 1
            logger.info(f"📤 Dodatkowy plik {additional_file} wysłany jako {s3_key}")
        else:
            logger.warning(f"Plik {additional_file} nie istnieje, nie został wysłany.")
    except Exception as e:
        logger.error(f"❌ Błąd podczas wysyłania dodatkowego pliku: {e}")

    return pd.DataFrame({"status": ["success"], "files_uploaded": [file_count]})


