import os
import pandas as pd
import re
from pathlib import Path


def extract_numbers_from_text(s, pattern):
    match = pattern.search(s)
    return int(match.group(1)) if match else float("inf")


def extract_numbers_from_folder(path):
    folder_pattern = re.compile(r"target(\d+)_(\d+)")
    match = folder_pattern.search(str(path))
    return (
        (int(match.group(1)), int(match.group(2)))
        if match
        else (float("inf"), float("inf"))
    )


def remove_duplicates_in_join(df, columns):
    """
    For a prettier Join sheet: leave repeated values blank for specified columns.
    """
    for col in columns:
        df[col] = df[col].where(df[col].ne(df[col].shift()), "")
    return df


def change_target_source_name(df):
    df["Target Data Name"] = "Target" + df["Target Data Name"].str[6:]
    df["Source Data Name"] = (
        "Source" + df["Target Data Name"].str[6:] + "_" + df["Source Data Name"].str[5:]
    )
    return df


def _map_dtype_to_simple(dtype_str: str) -> str:
    """
    Map pandas dtype string to simplified logical type
    (string | integer | float | timestamp | boolean), defaulting to the original dtype string.
    """
    s = dtype_str.lower()
    if "datetime" in s:
        return "timestamp"
    if "bool" in s:
        return "boolean"
    if "float" in s:
        return "float"
    # cover pandas nullable ints (Int64), unsigned, and regular ints
    if s.startswith("int") or s.startswith("uint") or "int" in s:
        return "integer"
    if "string" in s or "object" in s or "category" in s:
        return "string"
    return dtype_str


def get_schema_with_types_pairs(df: pd.DataFrame):
    """
    Return list of (column, simple_type) pairs.
    """
    pairs = []
    for col, dtype in df.dtypes.items():
        pairs.append((col, _map_dtype_to_simple(str(dtype))))
    return pairs


def format_schema_with_types_str(pairs):
    """
    Format as: "['col1': type1, 'col2': type2, ...]"
    """
    return "[" + ", ".join([f"'{c}': {t}" for c, t in pairs]) + "]"


# === Configure your base directory here ===
base_directory = Path(
    r"/home/local/ASUAD/jrtandel/transchema/autopipeline-benchmarks/github-pipelines"
)

# Initialize a dictionary to store data
data = {}

test_pattern = re.compile(r"test_(\d+)")

# Iterate through the subdirectories
for folder in sorted(base_directory.iterdir(), key=extract_numbers_from_folder):
    if folder.is_dir():
        target_csv_path = folder / "target.csv"
        if target_csv_path.exists():
            # For target.csv
            target_df = pd.read_csv(target_csv_path, low_memory=False)
            # Drop unnamed index-like columns if present
            target_df = target_df.loc[:, ~target_df.columns.str.contains("^Unnamed")]
            target_sample = (
                [[]] if target_df.empty else target_df.head(3).values.tolist()
            )
            target_header = [] if target_df.empty else target_df.columns.tolist()

            # Build target schema with types
            target_pairs = (
                [] if target_df.empty else get_schema_with_types_pairs(target_df)
            )
            target_schema_with_types = (
                format_schema_with_types_str(target_pairs) if target_pairs else "[]"
            )

            data[folder.name] = {
                "Target Data Schema": target_header,
                "Target Data Schema with Types": target_schema_with_types,
                "Target Data Sample": target_sample,
                "Test Files": [],
            }

            # Collect test/source CSVs
            test_csv_files = [
                file
                for file in folder.iterdir()
                if file.name.startswith("test_") and file.name.endswith(".csv")
            ]
            for test_csv_file in test_csv_files:
                # For test/source CSVs
                test_df = pd.read_csv(test_csv_file, low_memory=False)
                test_df = test_df.loc[:, ~test_df.columns.str.contains("^Unnamed")]
                test_sample = [[]] if test_df.empty else test_df.head(3).values.tolist()
                test_columns = test_df.columns.tolist()

                # Build source schema with types
                source_pairs = (
                    get_schema_with_types_pairs(test_df) if not test_df.empty else []
                )
                source_schema_with_types = (
                    format_schema_with_types_str(source_pairs) if source_pairs else "[]"
                )

                data[folder.name]["Test Files"].append(
                    (
                        test_csv_file.name,
                        test_sample,
                        test_columns,
                        source_schema_with_types,
                    )
                )

# Prepare DataFrame
df_rows = []
for folder_name, contents in data.items():
    for file_name, sample, columns, src_schema_types in sorted(
        contents["Test Files"],
        key=lambda x: extract_numbers_from_text(x[0], test_pattern),
    ):
        df_rows.append(
            {
                "Target Data Name": folder_name,
                "Target Data Schema": contents["Target Data Schema"],
                "Target Data Schema with Types": contents[
                    "Target Data Schema with Types"
                ],
                "Target Data Sample": contents["Target Data Sample"],
                "Source Data Name": file_name[:-4],
                "Source Data Schema": columns,
                "Source Data Schema with Types": src_schema_types,
                "3 Samples of Source Data": sample,
            }
        )

df = pd.DataFrame(df_rows)

# Identify join vs non-join (multiple test files per target)
df["Test File Count"] = df.groupby("Target Data Name")["Target Data Name"].transform(
    "count"
)
df_join = df[df["Test File Count"] > 1].copy()
df_non_join = df[df["Test File Count"] == 1].copy()

# Human-friendly names
df_join = change_target_source_name(df_join)
df_non_join = change_target_source_name(df_non_join)
df = change_target_source_name(df)

# For Join sheet, blank out repeated target info across rows, including new type column
df_join = remove_duplicates_in_join(
    df_join,
    [
        "Target Data Name",
        "Target Data Schema",
        "Target Data Schema with Types",
        "Target Data Sample",
    ],
)

# Clean up helper column
df.drop(columns=["Test File Count"], inplace=True)
df_join.drop(columns=["Test File Count"], inplace=True, errors="ignore")
df_non_join.drop(columns=["Test File Count"], inplace=True, errors="ignore")

# Output Excel
output_excel_path = base_directory / "output.xlsx"

try:
    with pd.ExcelWriter(output_excel_path) as writer:
        df.to_excel(writer, sheet_name="All_Data", index=False)
        df_join.to_excel(writer, sheet_name="Join", index=False)
        df_non_join.to_excel(writer, sheet_name="Non_Join", index=False)
    print(f"Data saved to {output_excel_path}")
except Exception as e:
    print(f"Error occurred while saving data: {e}")
