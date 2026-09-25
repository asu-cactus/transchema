import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

# Group by 'crit_cn' and count non-null 'critic' entries per country
result = df0.groupby('crit_cn', as_index=False).agg({'critic': 'count'})

# Ensure 'critic' column is integer type
result['critic'] = result['critic'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)