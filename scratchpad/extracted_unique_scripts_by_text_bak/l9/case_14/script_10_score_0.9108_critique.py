import pandas as pd

# Read all sources with index_col=0 to ignore the first numerical index column
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_14/training_9.csv", index_col=0)

# Rename SalePrice columns to match target schema exactly
s0 = s0.rename(columns={"SalePrice": "SalePrice_x"})
s1 = s1.rename(columns={"SalePrice": "SalePrice_y"})
s2 = s2.rename(columns={"SalePrice": "SalePrice_y_4"})
s3 = s3.rename(columns={"SalePrice": "SalePrice_x_3"})
s4 = s4.rename(columns={"SalePrice": "SalePrice_x_5"})
s5 = s5.rename(columns={"SalePrice": "SalePrice_y_6"})
s6 = s6.rename(columns={"SalePrice": "SalePrice_x_7"})
s7 = s7.rename(columns={"SalePrice": "SalePrice_y_8"})
s8 = s8.rename(columns={"SalePrice": "SalePrice_x_9"})
s9 = s9.rename(columns={"SalePrice": "SalePrice_y_10"})

# Merge all dataframes on 'Id' using inner joins
df = s0.merge(s1, on="Id") \
       .merge(s2, on="Id") \
       .merge(s3, on="Id") \
       .merge(s4, on="Id") \
       .merge(s5, on="Id") \
       .merge(s6, on="Id") \
       .merge(s7, on="Id") \
       .merge(s8, on="Id") \
       .merge(s9, on="Id")

# Reorder columns exactly as in target schema
df = df[['Id', 'SalePrice_x', 'SalePrice_y', 'SalePrice_x_3', 'SalePrice_y_4', 
         'SalePrice_x_5', 'SalePrice_y_6', 'SalePrice_x_7', 'SalePrice_y_8', 
         'SalePrice_x_9', 'SalePrice_y_10']]

# Write output CSV without index
df.to_csv("autopipeline-benchmarks/github-pipelines/length9_14/target_multisource_mcts.csv", index=False)