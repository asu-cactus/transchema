import pandas as pd

# Read the source CSV file
source0_path = "autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv"
df0 = pd.read_csv(source0_path, index_col=0)

# Group by 'sex' and 'smoker' and aggregate mean of 'total_bill', 'tip', and 'size'
result = df0.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write the result to the target CSV file
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)