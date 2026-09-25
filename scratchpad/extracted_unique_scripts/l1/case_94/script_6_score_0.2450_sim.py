import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, left_on="Store", right_on="shop_id", how="inner")

merged = merged.rename(columns={"Store": "Store", "Dept": "Dept", "Date": "Date", "Weekly_Sales": "Weekly_Sales", "IsHoliday": "IsHoliday", "ID": "ID", "shop_id": "shop_id", "item_id": "item_id"})

merged = merged[["Store", "Dept", "Date", "Weekly_Sales", "IsHoliday", "ID", "shop_id", "item_id"]]

merged["Store"] = pd.to_numeric(merged["Store"], errors='coerce')
merged["Dept"] = pd.to_numeric(merged["Dept"], errors='coerce')
merged["Weekly_Sales"] = pd.to_numeric(merged["Weekly_Sales"], errors='coerce')
merged["ID"] = pd.to_numeric(merged["ID"], errors='coerce')
merged["shop_id"] = pd.to_numeric(merged["shop_id"], errors='coerce')
merged["item_id"] = pd.to_numeric(merged["item_id"], errors='coerce')
merged["Date"] = merged["Date"].astype(str)
merged["IsHoliday"] = merged["IsHoliday"].astype(str)

merged.to_csv("autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv", index=False)