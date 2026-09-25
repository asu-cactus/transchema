import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

# The partial plan suggests joining Source1_93_0 with itself on user_id and time, which is redundant here since it's the same table.
# The PIVOT operation is ambiguous given the source schema matches target schema.
# Since source schema matches target schema, no join or pivot is actually needed.
# We just need to ensure correct dtypes and save.

df = df0.copy()

df['user_id'] = df['user_id'].astype(str)
df['time'] = df['time'].astype(str)
df['bet'] = pd.to_numeric(df['bet'], errors='coerce')
df['win'] = pd.to_numeric(df['win'], errors='coerce')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)