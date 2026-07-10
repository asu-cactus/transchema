import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length4_85/training_0.csv"
df0 = pd.read_csv(source_path, index_col=0)

# Group by 'crit_cn' and count distinct 'critic' values
df_result = df0.groupby('crit_cn', as_index=False).agg({'critic': pd.Series.nunique})

# Ensure 'critic' column is integer type
df_result['critic'] = df_result['critic'].astype(int)

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_mcts.csv", index=False)