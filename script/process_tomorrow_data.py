import os
import json
import glob
import argparse


KEYS_TO_KEEP = {
    "humidity",
    "temperature",
    "dewPoint",
    "evapotranspiration",
    "uvIndex",
    "uvHealthConcern",
    "temperatureApparent",
    "windSpeed",
    "windGust",
    "visibility",
    "cloudCover",
}


def main(output_file: str):
    directory = "data/recent-history"

    data_by_time = {}

    # Read all json files in the directory
    for filepath in glob.glob(os.path.join(directory, "*.json")):
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {filepath}")
                continue

            # The exact structure depends on the API, based on the file we see:
            # {"timelines": {"hourly": [{"time": "...", "values": {...}}, ...]}}
            if "timelines" in data and "hourly" in data["timelines"]:
                entries = data["timelines"]["hourly"]
            elif isinstance(data, list):
                entries = data
            elif "time" in data and ("values" in data or "Values" in data):
                entries = [data]
            else:
                entries = []

            for entry in entries:
                time_val = entry.get("time")
                values = entry.get("values", entry.get("Values", {}))

                if time_val and values:
                    filtered_values = {
                        k: v for k, v in values.items() if k in KEYS_TO_KEEP
                    }
                    # Deduplicate by overwriting or keeping the first one.
                    # Overwriting is generally fine as the newer files might have updated forecasts/actuals.
                    data_by_time[time_val] = filtered_values

    # Format output as requested
    output = []
    for time_val in sorted(data_by_time.keys()):
        output.append({"time": time_val, "Values": data_by_time[time_val]})

    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)

    print(
        f"Successfully processed {len(output)} deduplicated time entries. Saved to {output_file}"
    )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-o", type=str, required=True)
    args = argparser.parse_args()
    main(args.o)
