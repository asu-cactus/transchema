import pandas as pd

# Read sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_1/training_3.csv", index_col=0)

# Rename columns to target schema names
s0 = s0.rename(columns={"Wins": "2013 Wins", "Losses": "2013 Losses", "Draws": "2013 Draws"})
s1 = s1.rename(columns={"Wins": "2014 Wins", "Losses": "2014 Losses", "Draws": "2014 Draws"})
s2 = s2.rename(columns={"Wins": "2015 Wins", "Losses": "2015 Losses", "Draws": "2015 Draws"})
s3 = s3.rename(columns={"Wins": "2016 Wins", "Losses": "2016 Losses", "Draws": "2016 Draws"})

# Aggregate each source by Wrestler to ensure uniqueness
s0_agg = s0.groupby("Wrestler", as_index=False).sum()
s1_agg = s1.groupby("Wrestler", as_index=False).sum()
s2_agg = s2.groupby("Wrestler", as_index=False).sum()
s3_agg = s3.groupby("Wrestler", as_index=False).sum()

# Join all aggregated sources on Wrestler using outer join to keep all wrestlers
join_0_1 = pd.merge(s0_agg, s1_agg, on="Wrestler", how="outer")
join_0_1_2 = pd.merge(join_0_1, s2_agg, on="Wrestler", how="outer")
final_df = pd.merge(join_0_1_2, s3_agg, on="Wrestler", how="outer")

# Convert columns to Int64 to match target schema (nullable integer)
final_df = final_df.astype({
    '2013 Wins': 'Int64', '2013 Losses': 'Int64', '2013 Draws': 'Int64',
    '2014 Wins': 'Int64', '2014 Losses': 'Int64', '2014 Draws': 'Int64',
    '2015 Wins': 'Int64', '2015 Losses': 'Int64', '2015 Draws': 'Int64',
    '2016 Wins': 'Int64', '2016 Losses': 'Int64', '2016 Draws': 'Int64'
})

# Write output
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_1/target_multisource_mcts.csv", index=False)