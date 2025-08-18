import pandas as pd
import json
from datetime import datetime


def convert_datetime(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def convert_excel_to_json(excel_file_path, json_file_path):
    # Read the Excel file
    xls = pd.ExcelFile(excel_file_path)

    # Specify the columns to include in the JSON file
    columns_to_include = [
        "Target Data Name",
        "Target Data Schema",
        "Target Data Schema with Types",
        "Target Data Sample",
        "Source Data Name",
        "Source Data Schema",
        "Source Data Schema with Types",
        "3 Samples of Source Data",
    ]

    # Read the specified columns from the Non_Join sheet
    data_to_convert = pd.read_excel(xls, sheet_name="Join", usecols=columns_to_include)

    # Fill missing values for target-related columns
    columns_to_fill = [
        "Target Data Name",
        "Target Data Schema",
        "Target Data Schema with Types",
        "Target Data Sample",
    ]
    data_to_convert[columns_to_fill] = data_to_convert[columns_to_fill].ffill()

    # Convert rows to dict
    json_data = [row.to_dict() for _, row in data_to_convert.iterrows()]

    # Save to JSON
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(
            json_data, json_file, indent=4, default=convert_datetime, ensure_ascii=False
        )

    print(f"✅ JSON file has been saved to {json_file_path}")


# Path to the Excel file
excel_file_path = r"/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines/output.xlsx"

# Path to save the JSON file
json_file_path = "/home/local/ASUAD/jrtandel/transchema/data/chatgpt_github_ms.json"

# Run conversion
convert_excel_to_json(excel_file_path, json_file_path)
