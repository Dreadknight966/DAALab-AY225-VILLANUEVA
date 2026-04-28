import json
import os
import re

def process_wdi_data(input_filename, output_path):
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    summary_stats = []

    # Regex to find keys like "Series changes 2019"
    year_pattern = re.compile(r"Series changes (\d{4})")

    # Sort keys to ensure the timeline goes in order
    sorted_keys = sorted([k for k in raw_data.keys() if year_pattern.match(k)])

    for key in sorted_keys:
        year = year_pattern.search(key).group(1)
        entries = raw_data[key]
        
        # Initialize counts for this year
        stats = {
            "Year": year,
            "New Indicators": 0,
            "Retired Indicators": 0,
            "Metadata Updates": 0
        }

        for entry in entries:
            # Skip nulls and header rows
            if not entry or entry.get("Cat") == "Cat" or "Cat" not in entry:
                continue
            
            cat = entry["Cat"].strip()
            
            if cat == "Add":
                stats["New Indicators"] += 1
            elif cat == "Del":
                stats["Retired Indicators"] += 1
            else:
                # Includes 'Des' (Description), 'Cod' (Code), 'Def' (Definition), etc.
                stats["Metadata Updates"] += 1

        summary_stats.append(stats)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, indent=2)

    print(f"Successfully processed {len(summary_stats)} years of data.")
    print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    # Change 'application.json' to your actual filename if different
    process_wdi_data('application.json', './assets/data.json')