import pandas as pd

# Read source tables
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

# Rename columns to match target year columns
df0 = df0.rename(columns={
    "Wins": "2016 Wins",
    "Losses": "2016 Losses",
    "Draws": "2016 Draws"
})

df1 = df1.rename(columns={
    "Wins": "2015 Wins",
    "Losses": "2015 Losses",
    "Draws": "2015 Draws"
})

df2 = df2.rename(columns={
    "Wins": "2014 Wins",
    "Losses": "2014 Losses",
    "Draws": "2014 Draws"
})

df3 = df3.rename(columns={
    "Wins": "2013 Wins",
    "Losses": "2013 Losses",
    "Draws": "2013 Draws"
})

# Join all tables on Wrestler using outer joins to keep all wrestlers
result = pd.merge(df3, df2, on="Wrestler", how="outer")
result = pd.merge(result, df1, on="Wrestler", how="outer")
result = pd.merge(result, df0, on="Wrestler", how="outer")

# Reorder columns to match target schema
cols = ["Wrestler",
        "2013 Wins", "2013 Losses", "2013 Draws",
        "2014 Wins", "2014 Losses", "2014 Draws",
        "2015 Wins", "2015 Losses", "2015 Draws",
        "2016 Wins", "2016 Losses", "2016 Draws"]

result = result[cols]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)