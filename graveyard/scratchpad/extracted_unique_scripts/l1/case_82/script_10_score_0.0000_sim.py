import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df_pivot = df0.drop(columns=['category', 'common_names'])
df_pivot = df_pivot.dropna(subset=['conservation_status', 'scientific_name'])
df_pivot['scientific_name'] = pd.to_numeric(df_pivot['scientific_name'], errors='coerce')
df_pivot = df_pivot.dropna(subset=['scientific_name'])
df_pivot['scientific_name'] = df_pivot['scientific_name'].astype(int)

result = df_pivot.groupby('conservation_status', as_index=False)['scientific_name'].count()
result.columns = ['conservation_status', 'scientific_name']

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)