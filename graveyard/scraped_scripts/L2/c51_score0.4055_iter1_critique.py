import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_51/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="Mouse ID", how="inner")

# Extract digits from Mouse ID strings to convert to integer
mouse_id_int = merged["Mouse ID"].astype(str).str.extract('(\d+)', expand=False)
merged = merged.assign(**{"Mouse ID": pd.to_numeric(mouse_id_int, errors='coerce')})

# Drop rows where Mouse ID could not be converted to int
merged = merged.dropna(subset=["Mouse ID"])

# Convert to int type
merged = merged.assign(**{"Mouse ID": merged["Mouse ID"].astype(int)})

# Convert Timepoint to int (already int but ensure)
merged = merged.assign(**{"Timepoint": merged["Timepoint"].astype(int)})

# Group by Drug, Timepoint, Mouse ID to remove duplicates
grouped = merged.groupby(["Drug", "Timepoint", "Mouse ID"], as_index=False).size()

# grouped has columns: Drug, Timepoint, Mouse ID, size
# We only need the group by columns as output
result = grouped[["Drug", "Timepoint", "Mouse ID"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_51/target_multisource_mcts.csv", index=False)