import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_74/training_0.csv", index_col=0)

agg_df = df0.groupby("Gender").agg({
    "Purchase ID": "sum",
    "SN": "count",
    "Age": pd.Series.nunique,
    "Item ID": pd.Series.nunique,
    "Item Name": pd.Series.nunique,
    "Price": pd.Series.nunique
}).reset_index()

agg_df.rename(columns={
    "SN": "SN",
    "Age": "Age",
    "Item ID": "Item ID",
    "Item Name": "Item Name",
    "Price": "Price"
}, inplace=True)

agg_df = agg_df.astype({
    "Purchase ID": "int64",
    "SN": "int64",
    "Age": "int64",
    "Item ID": "int64",
    "Item Name": "int64",
    "Price": "int64",
    "Gender": "string"
})

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_74/target_multisource_mcts.csv", index=False)