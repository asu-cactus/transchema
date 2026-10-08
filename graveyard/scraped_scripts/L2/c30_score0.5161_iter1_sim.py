import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_30/training_1.csv", index_col=0)

df0_unpivoted = pd.melt(df0, id_vars=['city'], value_vars=['driver_count', 'type'], var_name='variable', value_name='fare')
df0_unpivoted = df0_unpivoted[df0_unpivoted['variable'] == 'driver_count'].copy()
df0_unpivoted['fare'] = pd.to_numeric(df0_unpivoted['fare'], errors='coerce')
df0_unpivoted = df0_unpivoted[['city', 'fare']].dropna(subset=['fare'])

df1_filtered = df1[['city', 'fare']].copy()
df1_filtered['fare'] = pd.to_numeric(df1_filtered['fare'], errors='coerce')
df1_filtered = df1_filtered.dropna(subset=['fare'])

result = pd.concat([df0_unpivoted, df1_filtered], ignore_index=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length2_30/target_multisource_mcts.csv", index=False)