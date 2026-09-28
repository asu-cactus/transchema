import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_74/training_1.csv", index_col=0)

# Join on Mouse ID
merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Filter rows where Mouse ID can be converted to int
def can_convert_int(val):
    try:
        int(val)
        return True
    except:
        return False

filtered = merged[merged["Mouse ID"].apply(can_convert_int)].copy()

# Convert Mouse ID to int
filtered["Mouse ID"] = filtered["Mouse ID"].astype(int)

# Select columns in target schema order
result = filtered[["Drug", "Timepoint", "Mouse ID"]].copy()

# Ensure Timepoint is int
result["Timepoint"] = result["Timepoint"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_74/target_multisource_mcts.csv", index=False)