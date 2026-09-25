import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length3_62/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length3_62/training_3.csv",
]

# Read all source tables
dfs = [pd.read_csv(p, index_col=0) for p in paths]

# Rename columns in each df to match target schema columns for the corresponding year
year_cols = {
    0: ['2013 Wins', '2013 Losses', '2013 Draws'],
    1: ['2014 Wins', '2014 Losses', '2014 Draws'],
    2: ['2015 Wins', '2015 Losses', '2015 Draws'],
    3: ['2016 Wins', '2016 Losses', '2016 Draws'],
}

for i, df in enumerate(dfs):
    df.columns = ['Wrestler'] + year_cols[i]

# Join all dataframes on 'Wrestler'
df_joined = dfs[0]
for df in dfs[1:]:
    df_joined = df_joined.merge(df, on='Wrestler', how='outer')

# Fill missing values with 0 and convert to int for all year-result columns
int_cols = df_joined.columns.drop('Wrestler')
df_joined[int_cols] = df_joined[int_cols].fillna(0).astype(int)

# Write output with exact target schema column order
target_columns = ['Wrestler',
                  '2013 Wins', '2013 Losses', '2013 Draws',
                  '2014 Wins', '2014 Losses', '2014 Draws',
                  '2015 Wins', '2015 Losses', '2015 Draws',
                  '2016 Wins', '2016 Losses', '2016 Draws']

df_joined[target_columns].to_csv("autopipeline-benchmarks/github-pipelines/length3_62/target_multisource_mcts.csv", index=False)