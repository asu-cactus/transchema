import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df_grouped = df.groupby('B-day', as_index=False).agg({
    'ID Number': 'max',
    'Name': 'max',
    'Fed': 'max',
    'Sex': 'max'
})

df_grouped['Name_x'] = pd.to_numeric(df_grouped['Name'], errors='coerce')
df_grouped['Fed_x'] = pd.to_numeric(df_grouped['Fed'], errors='coerce')
df_grouped['Sex_x'] = pd.to_numeric(df_grouped['Sex'], errors='coerce')

result = df_grouped[['B-day', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x']].copy()
result = result.astype({
    'B-day': 'Int64',
    'ID Number': 'Int64',
    'Name_x': 'Int64',
    'Fed_x': 'Int64',
    'Sex_x': 'Int64'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)