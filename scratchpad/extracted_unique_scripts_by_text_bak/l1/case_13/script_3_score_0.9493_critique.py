import pandas as pd

# Read the source CSV with index_col=0 as per instructions
source = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv", index_col=0)

# Group by 'sex' and 'smoker' and aggregate mean of 'tip_pct'
result = source.groupby(['sex', 'smoker'], as_index=False).agg({'tip_pct': 'mean'})

# Write the result to the target CSV file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv", index=False)