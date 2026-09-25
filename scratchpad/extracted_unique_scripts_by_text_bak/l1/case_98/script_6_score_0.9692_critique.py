import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

# Join on Source0.right_index and Source1 index
result = pd.merge(df0, df1, left_on="right_index", right_index=True, how="inner")

# Rename columns to match target schema
result = result.rename(columns={"right_index": "0_x", "0_x": "0_x", "0_y": "0_y", "0_x": "0_x"})
# Actually, after merge, columns are: right_index, 0_x (from df0), 0_y (from df1)
# But df0 columns are right_index and 0, df1 columns are 0
# So after merge columns: right_index, 0_x (from df0's 0), 0_y (from df1's 0)
# We need to rename df0's 0 to 0_x and df1's 0 to 0_y before merge or after merge

# Let's rename before merge for clarity:
df0 = df0.rename(columns={"0": "0_x"})
df1 = df1.rename(columns={"0": "0_y"})

result = pd.merge(df0, df1, left_on="right_index", right_index=True, how="inner")

# Now drop right_index column and reorder columns as per target schema
result = result[["0_x", "0_y"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)