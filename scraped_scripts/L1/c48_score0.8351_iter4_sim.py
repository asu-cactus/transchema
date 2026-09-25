import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_48/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on='Text Date', right_on='Text Date')

df_grouped = df_joined.groupby('Text Date', as_index=False).agg({
    'Water Use_x': 'sum',
    'Power Use_x': 'sum'
})

df_grouped.rename(columns={'Text Date': 'Date', 'Water Use_x': 'Water Use', 'Power Use_x': 'Power Use'}, inplace=True)

df_grouped['Water Use'] = df_grouped['Water Use'].astype(float)
df_grouped['Power Use'] = df_grouped['Power Use'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_48/target_multisource_mcts.csv", index=False)