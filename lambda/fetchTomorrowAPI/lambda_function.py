import json
import os
import urllib.request
import boto3
from datetime import datetime


def lambda_handler(event, context):
    location = "51.47398329464333,-0.1828879798975107"
    api_key = os.getenv("tomorrow_apikey")
    bucket_name = "aiot-skin-gaurd"

    url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={api_key}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        file_name = f"realtime/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"

        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(data),
            ContentType="application/json",
        )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Successfully saved {file_name}"),
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps("Failed to capture data")}
