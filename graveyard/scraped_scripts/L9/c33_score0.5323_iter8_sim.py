import pandas as pd

paths = {
    "Source9_33_0": "autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv",
    "Source9_33_1": "autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv",
    "Source9_33_2": "autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv",
    "Source9_33_3": "autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv",
    "Source9_33_6": "autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv",
    "Source9_33_8": "autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv",
    "Source9_33_4": "autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv",
    "Source9_33_5": "autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv",
    "Source9_33_7": "autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv",
    "Source9_33_9": "autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv",
}

# Load the six source tables to unpivot (each has ROW_WID and one *_NUM column)
dfs_unpivot = []
for key in ["Source9_33_0", "Source9_33_1", "Source9_33_2", "Source9_33_3", "Source9_33_6", "Source9_33_8"]:
    df = pd.read_csv(paths[key], index_col=0)
    # Identify the numeric column (other than ROW_WID)
    num_col = [c for c in df.columns if c != "ROW_WID"][0]
    # Rename the numeric column to INTERACTIONS_NUM for unpivoting
    df_renamed = df.rename(columns={num_col: "INTERACTIONS_NUM"})
    dfs_unpivot.append(df_renamed[["INTERACTIONS_NUM"]])

# Concatenate all INTERACTIONS_NUM values vertically (UNPIVOT)
unpivoted = pd.concat(dfs_unpivot, ignore_index=True)

# GROUP_BY INTERACTIONS_NUM: count occurrences of each INTERACTIONS_NUM
result = unpivoted.groupby("INTERACTIONS_NUM", as_index=False).size()
result = result.rename(columns={"size": "COUNT"})

# The target schema only requires INTERACTIONS_NUM column, no count column.
# But target examples show only INTERACTIONS_NUM column with counts as values.
# So the target is just the distinct INTERACTIONS_NUM values, but the example shows counts as values.
# The partial plan says GROUP_BY : [INTERACTIONS_NUM], so likely the target is the counts per INTERACTIONS_NUM.
# But target schema is ['INTERACTIONS_NUM': integer], so the column is INTERACTIONS_NUM with counts as values.
# So we rename COUNT to INTERACTIONS_NUM to match target schema.

result = result.rename(columns={"COUNT": "INTERACTIONS_NUM"})

# Save the result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)