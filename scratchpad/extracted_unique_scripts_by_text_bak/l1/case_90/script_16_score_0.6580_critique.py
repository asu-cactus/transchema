import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_90/training_0.csv", index_col=0)

dog_stage_cols = ['doggo', 'floofer', 'pupper', 'puppo']

# Melt dog stage columns into long format
df_long = df.melt(value_vars=dog_stage_cols, var_name='dog_stage', value_name='flag')

# Keep only rows where flag is not null (dog stage present)
df_long = df_long[df_long['flag'].notna()]

# Group by dog_stage and count occurrences
counts = df_long.groupby('dog_stage').size().reset_index(name='count')

# Output only the counts as a single column dog_type
result = counts['count'].to_frame(name='dog_type')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_90/target_multisource_mcts.csv", index=False)