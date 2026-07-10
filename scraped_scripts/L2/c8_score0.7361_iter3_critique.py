import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_8/training_1.csv", index_col=0)

# Merge on Mouse ID (string)
merged = pd.merge(df0, df1, on="Mouse ID")

# Extract integer Mouse ID from string Mouse ID
# If no digits, drop those rows
mouse_id_int = merged["Mouse ID"].str.extract('(\d+)', expand=False)
merged = merged[mouse_id_int.notna()].copy()
merged["Mouse ID"] = mouse_id_int.astype(int)

# Group by Drug and Timepoint, aggregate count distinct Mouse ID
result = merged.groupby(["Drug", "Timepoint"], as_index=False).agg({"Mouse ID": pd.Series.nunique})

# Ensure types match target schema
result["Timepoint"] = result["Timepoint"].astype(int)
result["Mouse ID"] = result["Mouse ID"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_8/target_multisource_mcts.csv", index=False)