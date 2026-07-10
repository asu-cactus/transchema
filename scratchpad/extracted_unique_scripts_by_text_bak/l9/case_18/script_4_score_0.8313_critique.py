import pandas as pd

# Read all source tables
Source9_18_0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_0.csv", index_col=0)
Source9_18_1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_1.csv", index_col=0)
Source9_18_2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_2.csv", index_col=0)
Source9_18_3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_3.csv", index_col=0)
Source9_18_4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_4.csv", index_col=0)
Source9_18_5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_5.csv", index_col=0)
Source9_18_6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_6.csv", index_col=0)
Source9_18_7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_7.csv", index_col=0)
Source9_18_8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_8.csv", index_col=0)
Source9_18_9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_18/training_9.csv", index_col=0)

# Rename businesses and counts columns in the four similar schema tables to match target schema
Source9_18_9 = Source9_18_9.rename(columns={"businesses": "businesses_x", "counts": "counts_x"})
Source9_18_1 = Source9_18_1.rename(columns={"businesses": "businesses_y", "counts": "counts_y"})
Source9_18_3 = Source9_18_3.rename(columns={"businesses": "businesses_x_5", "counts": "counts_x_6"})
Source9_18_7 = Source9_18_7.rename(columns={"businesses": "businesses_y_7", "counts": "counts_y_8"})

# Rename counts columns in Source9_18_6 and Source9_18_8 to match target schema
Source9_18_6 = Source9_18_6.rename(columns={"counts": "counts_x_10"})
Source9_18_8 = Source9_18_8.rename(columns={"counts": "counts_y_11"})

# Merge all tables step by step on 'zipcode'
df = pd.merge(Source9_18_9, Source9_18_1, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_3, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_7, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_4, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_6, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_8, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_2, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_0, on="zipcode", how="inner")
df = pd.merge(df, Source9_18_5, on="zipcode", how="inner")

# Select and order columns exactly as in target schema
df = df[[
    "zipcode",
    "businesses_x", "counts_x",
    "businesses_y", "counts_y",
    "businesses_x_5", "counts_x_6",
    "businesses_y_7", "counts_y_8",
    "boro",
    "counts_x_10", "counts_y_11",
    "indicator",
    "counts",
    "total_crime",
    "violation",
    "misdemeanor",
    "felony",
    "theft",
    "assault",
    "harassment"
]]

# Write to output CSV
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_18/target_multisource_mcts.csv")