import os
import boto3
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("s3_bucket")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
)


def fetch_latest_json_from_s3(prefix):
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)

    latest_obj = None
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                if (
                    latest_obj is None
                    or obj["LastModified"] > latest_obj["LastModified"]
                ):
                    latest_obj = obj

    if not latest_obj:
        return None

    latest_key = latest_obj["Key"]

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
    data = fetch_latest_json_from_s3("realtime/")
    if not data:
        return None

    try:
        realtime_data = data.get("data", {})
        vals = realtime_data.get("values", {})

        return {
            "time": realtime_data.get("time"),
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


def get_indoor_history_24h():
    """Fetch all indoor sensor records from the last 24 hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=S3_BUCKET, Prefix="indoor/")

    records_by_time = {}
    for page in pages:
        if "Contents" not in page:
            continue
        for obj in page["Contents"]:
            try:
                resp = s3_client.get_object(Bucket=S3_BUCKET, Key=obj["Key"])
                data = json.loads(resp["Body"].read().decode("utf-8"))

                # Handle both list and single dict
                entries = data if isinstance(data, list) else [data]

                for entry in entries:
                    time_str = entry.get("timestamp") or entry.get("time")
                    if not time_str:
                        continue
                    try:
                        t = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if t < cutoff:
                        continue
                    vals = entry.get("values", entry)
                    temp = (
                        vals.get("temperature")
                        if isinstance(vals, dict)
                        else entry.get("temperature")
                    )
                    hum = (
                        vals.get("humidity")
                        if isinstance(vals, dict)
                        else entry.get("humidity")
                    )
                    if temp is not None and hum is not None:
                        records_by_time[time_str] = {
                            "time": time_str,
                            "temperature": temp,
                            "humidity": hum,
                        }
            except Exception as e:
                print(f"Error reading indoor history object {obj['Key']}: {e}")

    return sorted(records_by_time.values(), key=lambda x: x["time"])


def get_outdoor_history_24h():
    """Fetch all outdoor realtime records from the last 24 hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=S3_BUCKET, Prefix="realtime/")

    records_by_time = {}
    for page in pages:
        if "Contents" not in page:
            continue
        for obj in page["Contents"]:
            try:
                resp = s3_client.get_object(Bucket=S3_BUCKET, Key=obj["Key"])
                data = json.loads(resp["Body"].read().decode("utf-8"))

                # Realtime format: {"data": {"time": ..., "values": {...}}}
                realtime_data = data.get("data", {}) if isinstance(data, dict) else {}
                time_str = realtime_data.get("time")
                vals = realtime_data.get("values", {})

                if not time_str:
                    continue
                try:
                    t = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if t < cutoff:
                    continue

                temp = vals.get("temperature")
                hum = vals.get("humidity")
                if temp is not None and hum is not None:
                    records_by_time[time_str] = {
                        "time": time_str,
                        "temperature": temp,
                        "humidity": hum,
                        "uvIndex": vals.get("uvIndex"),
                        "windSpeed": vals.get("windSpeed"),
                        "cloudCover": vals.get("cloudCover"),
                        "dewPoint": vals.get("dewPoint"),
                    }
            except Exception as e:
                print(f"Error reading outdoor history object {obj['Key']}: {e}")

    return sorted(records_by_time.values(), key=lambda x: x["time"])


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
