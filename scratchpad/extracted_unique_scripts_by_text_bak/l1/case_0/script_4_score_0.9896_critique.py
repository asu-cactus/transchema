import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_0/training_0.csv", index_col=0)

# Clean State column by stripping whitespace
df['State'] = df['State'].str.strip()

# Filter out rows with NaN AverageTemperature
df = df[df['AverageTemperature'].notna()]

# Group by State and compute mean AverageTemperature
df_result = df.groupby('State', as_index=False)['AverageTemperature'].mean()

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_0/target_multisource_mcts.csv", index=False)