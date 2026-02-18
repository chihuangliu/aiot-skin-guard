import json
import boto3
from datetime import datetime

s3 = boto3.client("s3")
BUCKET_NAME = "aiot-skin-gaurd"


def lambda_handler(event, context):
    try:
        if "body" in event:
            payload = json.loads(event["body"])
        else:
            payload = event

        file_key = f"indoor/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=json.dumps(payload),
            ContentType="application/json",
        )

        print(f"Successfully saved data to {file_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Sensor data received", "file": file_key}),
        }

    except Exception as e:
        print(f"Error processing sensor data: {str(e)}")
        raise e
