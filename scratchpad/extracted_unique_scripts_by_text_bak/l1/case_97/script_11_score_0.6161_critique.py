import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_97/training_0.csv", index_col=0)

# Group by 'crit_cn' and count distinct 'critic' values per country
agg = df0.groupby('crit_cn', as_index=False).agg({'critic': pd.Series.nunique})

# Rename the aggregation column to 'critic' to match target schema
agg = agg.rename(columns={'critic': 'critic'})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_97/target_multisource_mcts.csv", index=False)