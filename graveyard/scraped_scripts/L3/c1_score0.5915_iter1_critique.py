import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

# Rename columns to match target schema for each year
df0 = df0.rename(columns={
    'Wins': '2013 Wins',
    'Losses': '2013 Losses',
    'Draws': '2013 Draws'
})

df1 = df1.rename(columns={
    'Wins': '2014 Wins',
    'Losses': '2014 Losses',
    'Draws': '2014 Draws'
})

df2 = df2.rename(columns={
    'Wins': '2015 Wins',
    'Losses': '2015 Losses',
    'Draws': '2015 Draws'
})

df3 = df3.rename(columns={
    'Wins': '2016 Wins',
    'Losses': '2016 Losses',
    'Draws': '2016 Draws'
})

# Join all four dataframes on 'Wrestler'
df_01 = pd.merge(df0, df1, on='Wrestler', how='outer')
df_02 = pd.merge(df_01, df2, on='Wrestler', how='outer')
df_final = pd.merge(df_02, df3, on='Wrestler', how='outer')

# Fill NaN with 0 and convert to int for all numeric columns
num_cols = df_final.columns.drop('Wrestler')
df_final[num_cols] = df_final[num_cols].fillna(0).astype(int)

# Reorder columns to match target schema exactly
target_columns = [
    'Wrestler',
    '2013 Wins', '2013 Losses', '2013 Draws',
    '2014 Wins', '2014 Losses', '2014 Draws',
    '2015 Wins', '2015 Losses', '2015 Draws',
    '2016 Wins', '2016 Losses', '2016 Draws'
]
df_final = df_final[target_columns]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)