import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_20/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID")

result = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size()

result = result.rename(columns={"size": "Count"})

# The target schema is ['Drug': string, 'Timepoint': integer, 'Mouse ID': integer]
# We have Drug (string), Timepoint (int), Mouse ID (string currently)
# Convert Mouse ID to integer if possible, else keep as string (but target example shows integer)
# The source Mouse ID is string like 'n763', 'q787', so we cannot convert to int directly.
# But target example shows Mouse ID as integer, so we must convert Mouse ID strings to integers.
# Since source Mouse ID is string with letters and digits, we can extract digits only as integer Mouse ID.

def extract_int_id(s):
    import re
    digits = re.findall(r'\d+', s)
    return int(digits[0]) if digits else None

result["Mouse ID"] = result["Mouse ID"].map(extract_int_id)
result["Timepoint"] = result["Timepoint"].astype(int)
result["Drug"] = result["Drug"].astype(str)

# The target table has only these 3 columns, so drop any others
result = result[["Drug", "Timepoint", "Mouse ID"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_20/target_multisource_mcts.csv", index=False)