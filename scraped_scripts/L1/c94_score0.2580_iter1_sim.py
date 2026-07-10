import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

result = pd.merge(df0, df1, left_on="Store", right_on="shop_id", how="left")

result = result[["Store", "Dept", "Date", "Weekly_Sales", "IsHoliday", "ID", "shop_id", "item_id"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)