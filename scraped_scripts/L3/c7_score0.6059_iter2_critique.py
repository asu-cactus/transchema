import pandas as pd

# Read source tables with index_col=0 to ignore the first numerical index column
df_2013 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_1.csv", index_col=0)
df_2014 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_3.csv", index_col=0)
df_2015 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_2.csv", index_col=0)
df_2016 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_7/training_0.csv", index_col=0)

# Rename columns to match target schema for each year
df_2013 = df_2013.rename(columns={
    'Wins': '2013 Wins',
    'Losses': '2013 Losses',
    'Draws': '2013 Draws'
})

df_2014 = df_2014.rename(columns={
    'Wins': '2014 Wins',
    'Losses': '2014 Losses',
    'Draws': '2014 Draws'
})

df_2015 = df_2015.rename(columns={
    'Wins': '2015 Wins',
    'Losses': '2015 Losses',
    'Draws': '2015 Draws'
})

df_2016 = df_2016.rename(columns={
    'Wins': '2016 Wins',
    'Losses': '2016 Losses',
    'Draws': '2016 Draws'
})

# Join all dataframes on 'Wrestler' using inner join to keep only wrestlers present in all years
df_joined = df_2013.merge(df_2014, on='Wrestler', how='inner') \
                   .merge(df_2015, on='Wrestler', how='inner') \
                   .merge(df_2016, on='Wrestler', how='inner')

# If duplicates exist, group by Wrestler and sum all numeric columns
# This ensures uniqueness and matches target key constraints
numeric_cols = [col for col in df_joined.columns if col != 'Wrestler']
df_final = df_joined.groupby('Wrestler', as_index=False)[numeric_cols].sum()

# Reorder columns to match target schema exactly
target_columns = ['Wrestler',
                  '2013 Wins', '2013 Losses', '2013 Draws',
                  '2014 Wins', '2014 Losses', '2014 Draws',
                  '2015 Wins', '2015 Losses', '2015 Draws',
                  '2016 Wins', '2016 Losses', '2016 Draws']

# Add missing columns with 0 if any (unlikely here)
for col in target_columns:
    if col not in df_final.columns:
        df_final[col] = 0

df_final = df_final[target_columns]

# Write output CSV without index
df_final.to_csv("autopipeline-benchmarks/github-pipelines/length3_7/target_multisource_mcts.csv", index=False)