import argparse
import glob
import json
import os


def main():
    parser = argparse.ArgumentParser(description="Process indoor JSON data.")
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output JSON file."
    )
    args = parser.parse_args()

    input_dir = "data/indoor"

    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} not found.")
        return

    results = []
    # Use glob to find all json files
    for file_path in glob.glob(os.path.join(input_dir, "**/*.json"), recursive=True):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)

                # Handle both list of dicts and single dicts
                if isinstance(data, dict):
                    data = [data]

                for entry in data:
                    time_val = entry.get("timestamp") or entry.get("time")
                    temp_val = entry.get("temperature")
                    hum_val = entry.get("humidity")

                    if (
                        time_val is not None
                        and temp_val is not None
                        and hum_val is not None
                    ):
                        results.append(
                            {
                                "time": time_val,
                                "values": {
                                    "temperature": temp_val,
                                    "humidity": hum_val,
                                },
                            }
                        )
            except json.JSONDecodeError:
                print(f"Failed to decode JSON from {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Sort results by time
    results.sort(key=lambda x: x["time"])

    # Write to output file
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Successfully processed {len(results)} records and saved to {args.output}")


if __name__ == "__main__":
    main()
