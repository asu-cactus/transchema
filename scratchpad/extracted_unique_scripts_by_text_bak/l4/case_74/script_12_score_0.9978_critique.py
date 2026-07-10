import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

agg_df = df0.groupby("Gender").agg({
    "Purchase ID": pd.Series.nunique,
    "SN": pd.Series.nunique,
    "Age": pd.Series.nunique,
    "Item ID": pd.Series.nunique,
    "Item Name": pd.Series.nunique,
    "Price": pd.Series.nunique
}).reset_index()

agg_df.columns = ['Gender', 'Purchase ID', 'SN', 'Age', 'Item ID', 'Item Name', 'Price']

agg_df["Purchase ID"] = agg_df["Purchase ID"].astype(int)
agg_df["SN"] = agg_df["SN"].astype(int)
agg_df["Age"] = agg_df["Age"].astype(int)
agg_df["Item ID"] = agg_df["Item ID"].astype(int)
agg_df["Item Name"] = agg_df["Item Name"].astype(int)
agg_df["Price"] = agg_df["Price"].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)