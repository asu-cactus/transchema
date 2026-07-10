import pandas as pd

# Read all source files with index_col=0 to ignore the first numerical index column
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_4.csv", index_col=0)
df5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_5.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_6.csv", index_col=0)
df7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_7.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_8.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_9.csv", index_col=0)

# Reset index to make 'Id' a column for merging
df0 = df0.reset_index()
df1 = df1.reset_index()
df2 = df2.reset_index()
df3 = df3.reset_index()
df4 = df4.reset_index()
df5 = df5.reset_index()
df6 = df6.reset_index()
df7 = df7.reset_index()
df8 = df8.reset_index()
df9 = df9.reset_index()

# Rename SalePrice columns exactly as in target schema
df0 = df0.rename(columns={"SalePrice": "SalePrice_x"})
df1 = df1.rename(columns={"SalePrice": "SalePrice_y"})
df2 = df2.rename(columns={"SalePrice": "SalePrice_x_3"})
df3 = df3.rename(columns={"SalePrice": "SalePrice_y_4"})
df4 = df4.rename(columns={"SalePrice": "SalePrice_x_5"})
df5 = df5.rename(columns={"SalePrice": "SalePrice_y_6"})
df6 = df6.rename(columns={"SalePrice": "SalePrice_x_7"})
df7 = df7.rename(columns={"SalePrice": "SalePrice_y_8"})
df8 = df8.rename(columns={"SalePrice": "SalePrice_x_9"})
df9 = df9.rename(columns={"SalePrice": "SalePrice_y_10"})

# Perform inner joins on 'Id' to keep only common Ids across all tables
df = df0.merge(df1, on="Id", how="inner") \
        .merge(df2, on="Id", how="inner") \
        .merge(df3, on="Id", how="inner") \
        .merge(df4, on="Id", how="inner") \
        .merge(df5, on="Id", how="inner") \
        .merge(df6, on="Id", how="inner") \
        .merge(df7, on="Id", how="inner") \
        .merge(df8, on="Id", how="inner") \
        .merge(df9, on="Id", how="inner")

# Reorder columns to match target schema exactly
df = df[['Id', 'SalePrice_x', 'SalePrice_y', 'SalePrice_x_3', 'SalePrice_y_4', 
         'SalePrice_x_5', 'SalePrice_y_6', 'SalePrice_x_7', 'SalePrice_y_8', 
         'SalePrice_x_9', 'SalePrice_y_10']]

# Write to CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)