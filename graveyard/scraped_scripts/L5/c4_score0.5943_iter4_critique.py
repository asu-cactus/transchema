import pandas as pd

# Read sources
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

# Source2 lacks 'Inducted By', add it with NaN to match source0 schema for union
source2 = source2.copy()
source2['Inducted By'] = pd.NA

# UNION Source0 and Source2 on all columns (same schema now)
union_0_2 = pd.concat([source0, source2], ignore_index=True, sort=False)

# Join union_0_2 with source1 on Artist (inner join to avoid extra NaNs)
join_0_2_1 = pd.merge(union_0_2, source1, on="Artist", how="inner")

# Join the above with source3 on Artist (inner join)
join_all = pd.merge(join_0_2_1, source3, on="Artist", how="inner")

# Convert columns to proper types before aggregation
join_all["Year Inducted"] = pd.to_numeric(join_all["Year Inducted"], errors='coerce')
join_all["Years Waited"] = pd.to_numeric(join_all["Years Waited"], errors='coerce')
join_all["# of Years Nominated"] = pd.to_numeric(join_all["# of Years Nominated"], errors='coerce')
join_all["Influenced"] = pd.to_numeric(join_all["Influenced"], errors='coerce')
join_all["Certified Units (Millions)"] = pd.to_numeric(join_all["Certified Units (Millions)"], errors='coerce')

# Define aggregation functions:
# For numeric columns: mean
# For 'Inducted By' (string): take first non-null value per group

def first_non_null(series):
    return series.dropna().iloc[0] if not series.dropna().empty else pd.NA

agg_dict = {
    "Year Inducted": "mean",
    "Years Waited": "mean",
    "# of Years Nominated": "mean",
    "Inducted By": first_non_null,
    "Influenced": "mean",
    "Certified Units (Millions)": "mean"
}

grouped = join_all.groupby("Artist", as_index=False).agg(agg_dict)

# Cast numeric columns to correct types matching target schema
grouped["Year Inducted"] = grouped["Year Inducted"].astype(float)
grouped["Years Waited"] = grouped["Years Waited"].round().astype("Int64")
grouped["# of Years Nominated"] = grouped["# of Years Nominated"].round().astype("Int64")
grouped["Influenced"] = grouped["Influenced"].round().astype("Int64")
grouped["Certified Units (Millions)"] = grouped["Certified Units (Millions)"].astype(float)

# Reorder columns to match target schema exactly
result = grouped[[
    "Artist",
    "Year Inducted",
    "Years Waited",
    "# of Years Nominated",
    "Inducted By",
    "Influenced",
    "Certified Units (Millions)"
]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)