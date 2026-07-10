import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_8/training_3.csv", index_col=0)

# Aggregate each source by Wrestler to ensure uniqueness
df0_agg = df0.groupby("Wrestler", as_index=False).sum()
df1_agg = df1.groupby("Wrestler", as_index=False).sum()
df2_agg = df2.groupby("Wrestler", as_index=False).sum()
df3_agg = df3.groupby("Wrestler", as_index=False).sum()

# Rename columns to match target schema
df0_agg = df0_agg.rename(columns={"Wins": "2013 Wins", "Losses": "2013 Losses", "Draws": "2013 Draws"})
df1_agg = df1_agg.rename(columns={"Wins": "2014 Wins", "Losses": "2014 Losses", "Draws": "2014 Draws"})
df2_agg = df2_agg.rename(columns={"Wins": "2015 Wins", "Losses": "2015 Losses", "Draws": "2015 Draws"})
df3_agg = df3_agg.rename(columns={"Wins": "2016 Wins", "Losses": "2016 Losses", "Draws": "2016 Draws"})

# Join all aggregated tables on Wrestler using outer join to keep all wrestlers
df_merged = df0_agg.merge(df1_agg, on="Wrestler", how="outer")\
                   .merge(df2_agg, on="Wrestler", how="outer")\
                   .merge(df3_agg, on="Wrestler", how="outer")

# Select columns in target order
cols = ['Wrestler', '2013 Wins', '2013 Losses', '2013 Draws',
        '2014 Wins', '2014 Losses', '2014 Draws',
        '2015 Wins', '2015 Losses', '2015 Draws',
        '2016 Wins', '2016 Losses', '2016 Draws']

df_merged = df_merged[cols]

# Fill NaNs with 0 and convert to int for numeric columns
int_cols = cols[1:]
df_merged[int_cols] = df_merged[int_cols].fillna(0).astype(int)

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length3_8/target_multisource_mcts.csv", index=False)