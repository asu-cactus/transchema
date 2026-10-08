import pandas as pd
import re

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(df0, df1, on="Mouse ID")

# Extract integer Mouse ID from string Mouse ID
def extract_int_id(s):
    digits = re.findall(r'\d+', s)
    return int(digits[0]) if digits else None

merged["Mouse ID"] = merged["Mouse ID"].map(extract_int_id)

# Select and reorder columns as per target schema
result = merged[["Drug", "Timepoint", "Mouse ID"]]

# Convert types to match target schema
result["Drug"] = result["Drug"].astype(str)
result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].astype(int)

# Remove duplicates to match unique rows in target
result = result.drop_duplicates(subset=["Drug", "Timepoint", "Mouse ID"])

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_20/target_multisource_mcts.csv", index=False)