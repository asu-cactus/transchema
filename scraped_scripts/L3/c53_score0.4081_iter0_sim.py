import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df_grouped = df.groupby(['B-day', 'ID Number'], as_index=False).agg({
    'Name': 'max',
    'Fed': 'max',
    'Sex': 'max'
})

df_grouped.rename(columns={
    'Name': 'Name_x',
    'Fed': 'Fed_x',
    'Sex': 'Sex_x'
}, inplace=True)

df_grouped = df_grouped.astype({
    'B-day': 'int64',
    'ID Number': 'int64',
    'Name_x': 'int64',
    'Fed_x': 'int64',
    'Sex_x': 'int64'
}, errors='ignore')

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)