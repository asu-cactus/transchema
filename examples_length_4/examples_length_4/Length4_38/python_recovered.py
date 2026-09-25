import pandas as pd

# File paths for source tables
source0_path = "autopipeline-benchmarks/github-pipelines/length4_38/test_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length4_38/test_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length4_38/test_2.csv"
source3_path = "autopipeline-benchmarks/github-pipelines/length4_38/test_3.csv"
source4_path = "autopipeline-benchmarks/github-pipelines/length4_38/test_4.csv"

# Read source tables with index_col=0 to ignore the first (index) column
df0 = pd.read_csv(source0_path, index_col=0)  # has wide schema including placeID and many attributes except Rcuisine, Rpayment, parking_lot, hours, days
df1 = pd.read_csv(source1_path, index_col=0)  # ['placeID', 'parking_lot']
df2 = pd.read_csv(source2_path, index_col=0)  # ['placeID', 'Rcuisine']
df3 = pd.read_csv(source3_path, index_col=0)  # ['placeID', 'Rpayment'] but has multiple rows per placeID, with different Rpayment values
df4 = pd.read_csv(source4_path, index_col=0)  # ['placeID', 'hours', 'days'] but multiple rows per placeID for different day segments

# --- Transformation Plan ---
# 1. df3 and df4 have multiple rows per placeID. We need to aggregate Rpayment by combining multiple payments per placeID as one string joined by underscore.
# 2. For df4, hours and days are multiple rows per placeID; hours are rhythm segments; days are the valid days per segment.
#    We need to combine all hours segments and days segments per placeID as single strings (join with ;).
# 3. Join all dfs on placeID with outer join to keep all placeIDs and all info.
# 4. Ensure all columns are converted to target dtypes.
# 5. For missing columns in the merged data or columns not present in any source (none here), assign "?" or "" as a default string.
#
# Column mapping for join and final dataframe structure:
# - From df0: all columns except Rpayment, Rcuisine, parking_lot, hours, days
# - From df1: parking_lot
# - From df2: Rcuisine
# - From df3: Rpayment aggregated per placeID, joined by underscore (_)
# - From df4: hours aggregated by concatenating unique hours segments separated by space or ; similarly days concatenated by ; as appeared in target example.
#
# Then write the resulting dataframe with columns ordered as in the target schema.

# --- Step 1: Aggregate Rpayment per placeID (df3) ---
# Combine multiple payment types per placeID by joining unique Rpayment values with underscore
rpayment_agg = (
    df3.groupby('placeID')['Rpayment']
    .apply(lambda x: "_".join(sorted(set(x.dropna()))))
    .reset_index()
)

# --- Step 2: Aggregate hours and days per placeID (df4) ---
# There are multiple rows per placeID with hours and days per row.
# We want to join hours strings per placeID with spaces and days strings per placeID with semicolons to mimic examples.
# Looking at target examples hours values appear like "13:00-23:30;" multiple hours with ; at end for each segment.
# days appear like "Mon;Tue;Wed;Thu;Fri;", joining multiple rows essentially means concatenating all rows' hours with ; similarly days with no added duplicates.

# For hours: join unique hours strings with no additional separator except that each string ends with ";"
# For days: join unique days strings with no duplicates, join by ""
def aggregate_hours(x):
    # join unique hours segments, ensuring each segment ends with ';' (strip whitespace)
    segments = sorted(set(x.dropna()))
    # ensure each segment ends with ';'
    segments = [seg if seg.endswith(";") else seg + ";" for seg in segments]
    return " ".join(segments).strip()

def aggregate_days(x):
    # days are strings like "Mon;", "Sat;" etc.
    # Collect unique day tokens from all rows, then join unique day tokens separated by ;
    all_days = []
    for val in x.dropna():
        # split existing day strings by ;, filter out empties, collect all tokens
        tokens = [d for d in val.split(";") if d]
        all_days.extend(tokens)
    # Unique and keep order as appeared
    unique_days = []
    for d in all_days:
        if d not in unique_days:
            unique_days.append(d)
    return ";".join(unique_days) + ";" if unique_days else ""

hours_agg = df4.groupby("placeID")['hours'].agg(aggregate_hours).reset_index()
days_agg = df4.groupby("placeID")['days'].agg(aggregate_days).reset_index()

# --- Step 3: Merge all dataframes on placeID ---

# Start merge with df0
merged = df0.copy()

# Merge parking_lot
merged = merged.merge(df1, how='left', on='placeID')

# Merge Rcuisine
merged = merged.merge(df2, how='left', on='placeID')

# Merge aggregated Rpayment
merged = merged.merge(rpayment_agg, how='left', on='placeID')

# Merge aggregated hours
merged = merged.merge(hours_agg, how='left', on='placeID')

# Merge aggregated days
merged = merged.merge(days_agg, how='left', on='placeID')

# --- Step 4: Handle columns not from source0 ---

# The df0 already has many columns from target except for Rpayment, Rcuisine, parking_lot, hours, days which are merged.

# Target columns in order:
target_columns = [
    'placeID', 'Rpayment', 'latitude', 'longitude', 'the_geom_meter', 'name', 'address',
    'city', 'state', 'country', 'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code',
    'accessibility', 'price', 'url', 'Rambience', 'franchise', 'area', 'other_services',
    'Rcuisine', 'hours', 'days', 'parking_lot'
]

# Check if all columns are in merged; if not, add with default "?" or ""
for col in target_columns:
    if col not in merged.columns:
        merged[col] = "?"  # default unknown string

# Rename the columns that come from sources but might differ or be duplicated
# The Rpayment in df0 does not exist, we take from aggregated rpayment_agg as 'Rpayment'
# So ensure assignment: merged['Rpayment'] = merged['Rpayment'] from rpayment_agg merge
# This was done in merge, so no renaming needed.

# Explicit column type fixes and fill NaNs
# placeID as integer
merged['placeID'] = merged['placeID'].astype(int)

# latitude and longitude float
merged['latitude'] = pd.to_numeric(merged['latitude'], errors='coerce')
merged['longitude'] = pd.to_numeric(merged['longitude'], errors='coerce')

# For strings, fill NA with "?" except parking_lot which in example sometimes is "none"
str_cols = [
    'Rpayment', 'the_geom_meter', 'name', 'address', 'city', 'state', 'country',
    'fax', 'zip', 'alcohol', 'smoking_area', 'dress_code', 'accessibility',
    'price', 'url', 'Rambience', 'franchise', 'area', 'other_services', 'Rcuisine',
    'hours', 'days'
]
for c in str_cols:
    if c in merged.columns:
        merged[c] = merged[c].fillna("?").astype(str)

# parking_lot special: in examples it has "none" as valid string, default to "none" if missing
if 'parking_lot' in merged.columns:
    merged['parking_lot'] = merged['parking_lot'].fillna("none").astype(str)
else:
    merged['parking_lot'] = "none"

# Reorder columns to target schema
merged = merged[target_columns]

# Final type coercions to ensure match target schema:
# from target schema:
# placeID: int
# Rpayment: str
# latitude: float
# longitude: float
# the_geom_meter: str
# name: str
# address: str
# city: str
# state: str
# country: str
# fax: str
# zip: str
# alcohol: str
# smoking_area: str
# dress_code: str
# accessibility: str
# price: str
# url: str
# Rambience: str
# franchise: str
# area: str
# other_services: str
# Rcuisine: str
# hours: str
# days: str
# parking_lot: str

# Just to be safe, enforce types once more
merged = merged.astype({
    'placeID': 'int',
    'Rpayment': 'str',
    'latitude': 'float',
    'longitude': 'float',
    'the_geom_meter': 'str',
    'name': 'str',
    'address': 'str',
    'city': 'str',
    'state': 'str',
    'country': 'str',
    'fax': 'str',
    'zip': 'str',
    'alcohol': 'str',
    'smoking_area': 'str',
    'dress_code': 'str',
    'accessibility': 'str',
    'price': 'str',
    'url': 'str',
    'Rambience': 'str',
    'franchise': 'str',
    'area': 'str',
    'other_services': 'str',
    'Rcuisine': 'str',
    'hours': 'str',
    'days': 'str',
    'parking_lot': 'str'
})

# --- Step 5: Export the result ---
output_path = "autopipeline-benchmarks/github-pipelines/length4_38/target_multisource_cot.csv"
merged.to_csv(output_path, index=False)