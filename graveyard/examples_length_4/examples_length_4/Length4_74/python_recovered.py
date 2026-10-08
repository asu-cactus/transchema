import pandas as pd
import re

def str_to_int_hash(s, mod=10**9+7):
    """Convert string to a deterministic integer hash."""
    return abs(hash(s)) % mod

def extract_digits(s):
    """Extract digits from string s, return as int if found else None."""
    digits = re.findall(r'\d+', s)
    if digits:
        return int(''.join(digits))
    return None

def convert_sn(sn_value):
    """Convert SN string to int: try extract digits else use hash."""
    if pd.isna(sn_value):
        return 0
    digits_int = extract_digits(sn_value)
    if digits_int is not None:
        return digits_int
    return str_to_int_hash(str(sn_value))

def convert_item_name(item_name):
    """Convert item name string to int hash."""
    if pd.isna(item_name):
        return 0
    return str_to_int_hash(str(item_name))

def main():
    source_path = 'autopipeline-benchmarks/github-pipelines/length4_74/test_0.csv'
    target_path = 'autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_cot.csv'

    # Load source data, ignoring index column
    df = pd.read_csv(source_path, index_col=0)

    # Rename columns to match target order (Target columns):
    # ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']
    # Source columns: ['Purchase ID', 'SN', 'Age', 'Gender', 'Item ID', 'Item Name', 'Price']
    # We reorder by taking source columns and reindex:
    df = df[['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']]

    # Convert types according to target schema:
    # Gender: string (already string)
    df['Gender'] = df['Gender'].astype(str)

    # Purchase ID: integer
    df['Purchase ID'] = pd.to_numeric(df['Purchase ID'], errors='coerce').fillna(0).astype(int)

    # SN: convert string to int by digits extraction or hashing
    df['SN'] = df['SN'].apply(convert_sn).astype(int)

    # Age: integer
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)

    # Item ID: integer
    df['Item ID'] = pd.to_numeric(df['Item ID'], errors='coerce').fillna(0).astype(int)

    # Item Name: convert string to int hash
    df['Item Name'] = df['Item Name'].apply(convert_item_name).astype(int)

    # Price: integer, round floats
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0).round().astype(int)

    # Save final DataFrame to CSV
    df.to_csv(target_path)

if __name__ == "__main__":
    main()