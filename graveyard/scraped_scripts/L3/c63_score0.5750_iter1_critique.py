import pandas as pd

# Read source CSVs with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

def pivot_source(df, year):
    # Copy to avoid modifying original
    df = df.copy()
    # Rename columns to match target schema for the given year
    df.rename(columns={
        'Wins': f'{year} Wins',
        'Losses': f'{year} Losses',
        'Draws': f'{year} Draws'
    }, inplace=True)
    # Only keep Wrestler and renamed columns
    return df[['Wrestler', f'{year} Wins', f'{year} Losses', f'{year} Draws']]

# Pivot each source to have columns named as in target schema
p0 = pivot_source(df0, 2013)
p1 = pivot_source(df1, 2014)
p2 = pivot_source(df2, 2015)
p3 = pivot_source(df3, 2016)

# Join all on 'Wrestler' column using outer join to keep all wrestlers
df_merged = p0.merge(p1, on='Wrestler', how='outer') \
              .merge(p2, on='Wrestler', how='outer') \
              .merge(p3, on='Wrestler', how='outer')

# Fill missing values with 0 and convert to int for all year columns
year_cols = ['2013 Wins', '2013 Losses', '2013 Draws',
             '2014 Wins', '2014 Losses', '2014 Draws',
             '2015 Wins', '2015 Losses', '2015 Draws',
             '2016 Wins', '2016 Losses', '2016 Draws']

for col in year_cols:
    if col not in df_merged.columns:
        df_merged[col] = 0

df_merged[year_cols] = df_merged[year_cols].fillna(0).astype(int)

# Reorder columns to match target schema exactly
df_merged = df_merged[['Wrestler'] + year_cols]

# Write to output CSV without index
df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)