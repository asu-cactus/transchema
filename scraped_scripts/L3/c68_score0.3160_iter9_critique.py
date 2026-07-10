import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_68/training_3.csv", index_col=0)

# Rename columns to match target schema per year
df0 = df0.rename(columns={
    "Wins": "2013 Wins",
    "Losses": "2013 Losses",
    "Draws": "2013 Draws"
})

df1 = df1.rename(columns={
    "Wins": "2014 Wins",
    "Losses": "2014 Losses",
    "Draws": "2014 Draws"
})

df2 = df2.rename(columns={
    "Wins": "2015 Wins",
    "Losses": "2015 Losses",
    "Draws": "2015 Draws"
})

df3 = df3.rename(columns={
    "Wins": "2016 Wins",
    "Losses": "2016 Losses",
    "Draws": "2016 Draws"
})

# Join all sources on Wrestler using outer joins to keep all wrestlers
join_01 = pd.merge(df0, df1, on="Wrestler", how="outer")
join_012 = pd.merge(join_01, df2, on="Wrestler", how="outer")
final_df = pd.merge(join_012, df3, on="Wrestler", how="outer")

# Select columns in target schema order
final_df = final_df[[
    "Wrestler",
    "2013 Wins", "2013 Losses", "2013 Draws",
    "2014 Wins", "2014 Losses", "2014 Draws",
    "2015 Wins", "2015 Losses", "2015 Draws",
    "2016 Wins", "2016 Losses", "2016 Draws"
]]

# Write to output CSV
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_68/target_multisource_mcts.csv", index=False)