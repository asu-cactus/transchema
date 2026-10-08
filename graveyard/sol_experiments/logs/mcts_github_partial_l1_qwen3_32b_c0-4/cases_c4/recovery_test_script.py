import pandas as pd

# Load source data
source_path = "autopipeline-benchmarks/github-pipelines/length1_4/test_0.csv"
source_df = pd.read_csv(source_path, index_col=0)

# Group by 'fname' and count unique 'Slice n°'
result_df = source_df.groupby("fname", as_index=False)["Slice n°"].nunique().rename(columns={"Slice n°": "count_of_obs"})

# Save result
result_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_4/target_multisource_mcts_recovery_test_val.csv", index=False)