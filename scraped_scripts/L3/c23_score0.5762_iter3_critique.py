import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_23/training_3.csv", index_col=0)

# Rename columns to match target schema for each year
# We must assign years to each source table:
# Based on the target schema and example, and the number of rows in each source:
# Source1 (df1) has 165 rows, Source3 (df3) has 84 rows, Source0 (df0) has 120 rows, Source2 (df2) has 121 rows.
# The target has 50 rows, so many wrestlers appear in multiple years.
# The best guess (from the example and typical order) is:
# df1 -> 2013
# df3 -> 2014
# df2 -> 2015
# df0 -> 2016

df1 = df1.rename(columns={
    'Wins': '2013 Wins',
    'Losses': '2013 Losses',
    'Draws': '2013 Draws'
})

df3 = df3.rename(columns={
    'Wins': '2014 Wins',
    'Losses': '2014 Losses',
    'Draws': '2014 Draws'
})

df2 = df2.rename(columns={
    'Wins': '2015 Wins',
    'Losses': '2015 Losses',
    'Draws': '2015 Draws'
})

df0 = df0.rename(columns={
    'Wins': '2016 Wins',
    'Losses': '2016 Losses',
    'Draws': '2016 Draws'
})

# Merge all dataframes on 'Wrestler' using outer join to keep all wrestlers
df_merge = df1.merge(df3, on='Wrestler', how='outer') \
              .merge(df2, on='Wrestler', how='outer') \
              .merge(df0, on='Wrestler', how='outer')

# The target schema columns in order:
cols = ['Wrestler',
        '2013 Wins', '2013 Losses', '2013 Draws',
        '2014 Wins', '2014 Losses', '2014 Draws',
        '2015 Wins', '2015 Losses', '2015 Draws',
        '2016 Wins', '2016 Losses', '2016 Draws']

# Ensure all columns exist, fill missing with 0
for col in cols[1:]:
    if col not in df_merge.columns:
        df_merge[col] = 0

df_merge = df_merge[cols]

# Fill NaN with 0 for numeric columns (Wins, Losses, Draws)
df_merge.iloc[:, 1:] = df_merge.iloc[:, 1:].fillna(0).astype(int)

# Write output
df_merge.to_csv("autopipeline-benchmarks/github-pipelines/length3_23/target_multisource_mcts.csv", index=False)