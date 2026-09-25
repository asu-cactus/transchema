import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

# Group by 'crit_cn' and count distinct 'critic'
result = df0.groupby('crit_cn', as_index=False).agg({'critic': pd.Series.nunique})

# Rename columns to match target schema exactly
result.columns = ['crit_cn', 'critic']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)