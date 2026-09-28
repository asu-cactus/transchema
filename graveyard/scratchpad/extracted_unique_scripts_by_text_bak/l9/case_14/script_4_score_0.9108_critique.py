import pandas as pd

# Read CSVs without index_col=0 to keep 'Id' as a column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_0.csv")
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_1.csv")
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_2.csv")
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_3.csv")
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_4.csv")
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_5.csv")
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_6.csv")
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_7.csv")
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_8.csv")
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_9.csv")

# Rename SalePrice columns exactly as in target schema
s0 = s0.rename(columns={"SalePrice": "SalePrice_x"})
s1 = s1.rename(columns={"SalePrice": "SalePrice_y"})
s2 = s2.rename(columns={"SalePrice": "SalePrice_x_3"})
s3 = s3.rename(columns={"SalePrice": "SalePrice_y_4"})
s4 = s4.rename(columns={"SalePrice": "SalePrice_x_5"})
s5 = s5.rename(columns={"SalePrice": "SalePrice_y_6"})
s6 = s6.rename(columns={"SalePrice": "SalePrice_x_7"})
s7 = s7.rename(columns={"SalePrice": "SalePrice_y_8"})
s8 = s8.rename(columns={"SalePrice": "SalePrice_x_9"})
s9 = s9.rename(columns={"SalePrice": "SalePrice_y_10"})

# Merge all sources on 'Id' using inner join
df = s0.merge(s1, on="Id", how="inner") \
       .merge(s2, on="Id", how="inner") \
       .merge(s3, on="Id", how="inner") \
       .merge(s4, on="Id", how="inner") \
       .merge(s5, on="Id", how="inner") \
       .merge(s6, on="Id", how="inner") \
       .merge(s7, on="Id", how="inner") \
       .merge(s8, on="Id", how="inner") \
       .merge(s9, on="Id", how="inner")

# Ensure correct dtypes
df = df.astype({
    "Id": int,
    "SalePrice_x": float,
    "SalePrice_y": float,
    "SalePrice_x_3": float,
    "SalePrice_y_4": float,
    "SalePrice_x_5": float,
    "SalePrice_y_6": float,
    "SalePrice_x_7": float,
    "SalePrice_y_8": float,
    "SalePrice_x_9": float,
    "SalePrice_y_10": float,
})

# Save to CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)