import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, left_on="Dept", right_on="item_id", how="inner")

merged["Store"] = merged["Store"].astype(float)
merged["Dept"] = merged["Dept"].astype(float)
merged["Date"] = merged["Date"].astype(str)
merged["Weekly_Sales"] = merged["Weekly_Sales"].astype(float)
merged["IsHoliday"] = merged["IsHoliday"].astype(str)
merged["ID"] = merged["ID"].astype(float)
merged["shop_id"] = merged["shop_id"].astype(float)
merged["item_id"] = merged["item_id"].astype(float)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)