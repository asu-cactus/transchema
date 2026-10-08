import pandas as pd

# Read the source CSV file with index_col=0 to ignore the numerical index column
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_20/training_0.csv", index_col=0)

# Group by 'sex' and 'smoker' and aggregate the numeric columns by mean
result = df.groupby(['sex', 'smoker'], as_index=False).agg({
    'total_bill': 'mean',
    'tip': 'mean',
    'size': 'mean'
})

# Write the result to the target CSV file with exact column names as in the target schema
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_20/target_multisource_mcts.csv", index=False)