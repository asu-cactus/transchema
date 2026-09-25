import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_96/training_0.csv', index_col=0)

# Extract Publisher column
publisher_series = df0['Publisher']

# Map Publisher strings to integer IDs
publisher_ids, uniques = pd.factorize(publisher_series)

# Create DataFrame with Publisher as integer
result = pd.DataFrame({'Publisher': publisher_ids + 1})  # +1 to match example IDs starting at 1

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_96/target_multisource_mcts.csv', index=False)