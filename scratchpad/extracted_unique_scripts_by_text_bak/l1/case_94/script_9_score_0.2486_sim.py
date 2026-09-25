import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

result = pd.merge(df0, df1, left_on="Store", right_on="shop_id", how="inner")

result = result[["Store", "Dept", "Date", "Weekly_Sales", "IsHoliday", "ID", "shop_id", "item_id"]]

result["Store"] = result["Store"].astype(float)
result["Dept"] = result["Dept"].astype(float)
result["Date"] = result["Date"].astype(str)
result["Weekly_Sales"] = result["Weekly_Sales"].astype(float)
result["IsHoliday"] = result["IsHoliday"].astype(str)
result["ID"] = result["ID"].astype(float)
result["shop_id"] = result["shop_id"].astype(float)
result["item_id"] = result["item_id"].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)