import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length1_94/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length1_94/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_94/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on Store=shop_id and Dept=item_id
df_merged = pd.merge(df0, df1, left_on=["Store", "Dept"], right_on=["shop_id", "item_id"], how="left")

# Cast columns to match target schema types
df_result = pd.DataFrame()
df_result["Store"] = df_merged["Store"].astype(float)
df_result["Dept"] = df_merged["Dept"].astype(float)
df_result["Date"] = df_merged["Date"].astype(str)
df_result["Weekly_Sales"] = df_merged["Weekly_Sales"].astype(float)
df_result["IsHoliday"] = df_merged["IsHoliday"].astype(str)
df_result["ID"] = df_merged["ID"].astype(float)
df_result["shop_id"] = df_merged["shop_id"].astype(float)
df_result["item_id"] = df_merged["item_id"].astype(float)

df_result.to_csv(target_path, index=False)