import os
import boto3
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("s3_bucket")
s3_client = boto3.client("s3")


def fetch_latest_json_from_s3(prefix):
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    if "Contents" not in response:
        return None

    # Sort by LastModified to get the latest file
    sorted_objects = sorted(
        response["Contents"], key=lambda obj: obj["LastModified"], reverse=True
    )
    latest_key = sorted_objects[0]["Key"]

    obj_response = s3_client.get_object(Bucket=S3_BUCKET, Key=latest_key)
    data = json.loads(obj_response["Body"].read().decode("utf-8"))
    return data


def get_latest_indoor_data():
    data = fetch_latest_json_from_s3("indoor/")
    if not data:
        return None

    if isinstance(data, list) and len(data) > 0:
        entry = data[-1]  # Assuming chronological if list
    else:
        entry = data

    return {
        "time": entry.get("timestamp") or entry.get("time"),
        "temperature": entry.get("temperature"),
        "humidity": entry.get("humidity"),
    }


def get_latest_outdoor_data():
    data = fetch_latest_json_from_s3("recent-history/")
    if not data:
        return None

    try:
        hourly_data = data.get("timelines", {}).get("hourly", [])
        if not hourly_data:
            return None

        # Get the current/latest hour
        latest_entry = hourly_data[0]
        vals = latest_entry.get("values", {})
        return {
            "time": latest_entry.get("time"),
            "temperature": vals.get("temperature"),
            "humidity": vals.get("humidity"),
            "cloudCover": vals.get("cloudCover"),
            "windSpeed": vals.get("windSpeed"),
            "uvIndex": vals.get("uvIndex"),
            "dewPoint": vals.get("dewPoint"),
        }
    except Exception as e:
        print(f"Error parsing outdoor data: {e}")
        return None


def calculate_risk_factors(indoor, outdoor):
    if not indoor or not outdoor:
        return {}

    temp_shock = outdoor["temperature"] - indoor["temperature"]
    hum_shock = outdoor["humidity"] - indoor["humidity"]

    return {
        "thermal_shock": temp_shock,
        "humidity_shock": hum_shock,
        "spring_back_risk": indoor["humidity"]
        > 55,  # High indoor humidity leads to spring back
        "elasticity_boost": hum_shock > 0,  # Stepping into more humid environment
        "cloud_risk": outdoor["cloudCover"] > 70,  # High cloud cover drives water down
        "wind_crash_forecast": outdoor["windSpeed"]
        > 5.0,  # High wind removes indoor humidity
        "indoor_oil_risk": indoor["humidity"]
        > 55,  # Tradeoff: high indoor hum -> high baseline oil
        "uv_oil_risk": outdoor["uvIndex"] >= 5,  # High UV drives oil up
    }


if __name__ == "__main__":
    indoor = get_latest_indoor_data()
    outdoor = get_latest_outdoor_data()
    print("Latest Indoor:", indoor)
    print("Latest Outdoor:", outdoor)
    print("Risk Factors:", calculate_risk_factors(indoor, outdoor))
