import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_46/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on="Text Date", right_on="Value Date", suffixes=('_left', '_right'))

df_grouped = df_joined.groupby('Text Date_left', as_index=False).agg({
    'Water Use_left': 'sum',
    'Power Use_left': 'sum'
})

df_grouped.rename(columns={
    'Text Date_left': 'Date',
    'Water Use_left': 'Water Use',
    'Power Use_left': 'Power Use'
}, inplace=True)

df_grouped['Date'] = df_grouped['Date'].astype(str)
df_grouped['Water Use'] = df_grouped['Water Use'].astype(float)
df_grouped['Power Use'] = df_grouped['Power Use'].astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts.csv", index=False)