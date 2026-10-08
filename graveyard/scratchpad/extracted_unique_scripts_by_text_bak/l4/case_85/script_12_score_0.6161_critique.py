import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv", index_col=0)

df = df0[['crit_cn', 'critic']].copy()

# Convert critic to numeric, coercing errors to NaN, then drop NaNs to count valid critics
df['critic'] = pd.to_numeric(df['critic'], errors='coerce')

# Group by crit_cn and count non-null critic values
result = df.groupby('crit_cn', as_index=False).agg({'critic': 'count'})

# Ensure critic column is integer type
result['critic'] = result['critic'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)