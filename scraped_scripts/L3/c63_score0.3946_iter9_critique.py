import pandas as pd

# Read source CSVs with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_63/training_3.csv", index_col=0)

# Rename columns in each dataframe to match the target schema for each year
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

# Join all dataframes on 'Wrestler' using outer joins to keep all wrestlers
joined_01 = pd.merge(df0, df1, on="Wrestler", how="outer")
joined_012 = pd.merge(joined_01, df2, on="Wrestler", how="outer")
final_df = pd.merge(joined_012, df3, on="Wrestler", how="outer")

# Reorder columns to match target schema exactly
final_df = final_df[[
    "Wrestler",
    "2013 Wins", "2013 Losses", "2013 Draws",
    "2014 Wins", "2014 Losses", "2014 Draws",
    "2015 Wins", "2015 Losses", "2015 Draws",
    "2016 Wins", "2016 Losses", "2016 Draws"
]]

# Write the final dataframe to the target CSV file
final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_63/target_multisource_mcts.csv", index=False)