import pandas as pd
import os

base_folder = "autopipeline-benchmarks/github-pipelines/length9_62/"

# Load all source CSVs
dfs = []
for i in range(135):
    file_path = os.path.join(base_folder, f"training_{i}.csv")
    df = pd.read_csv(
        file_path,
        index_col=0  # Ignore the numerical index as specified in Hint 22
    )
    dfs.append(df)

# Union all sources
all_data = pd.concat(dfs, ignore_index=True)

# Group by and sum
grouped = all_data.groupby(["name", "sex"], as_index=False)["number"].sum()

# Write to target file
output_path = os.path.join(base_folder, "target_multisource_mcts_recovery_test_val.csv")
grouped.to_csv(output_path, index=False)