import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, how='inner', left_on=['B-day', 'ID Number'], right_on=['B-day', 'ID Number'], suffixes=('_x', '_y'))

grouped = merged.groupby(['B-day', 'ID Number'], as_index=False).agg({
    'Name_x': 'first',
    'Fed_x': 'first',
    'Sex_x': 'first'
})

grouped['B-day'] = grouped['B-day'].astype(int)
grouped['ID Number'] = grouped['ID Number'].astype(int)
grouped['Name_x'] = pd.to_numeric(grouped['Name_x'], errors='coerce').fillna(0).astype(int)
grouped['Fed_x'] = pd.to_numeric(grouped['Fed_x'], errors='coerce').fillna(0).astype(int)
grouped['Sex_x'] = pd.to_numeric(grouped['Sex_x'], errors='coerce').fillna(0).astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)