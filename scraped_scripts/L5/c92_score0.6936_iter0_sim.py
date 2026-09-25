import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

agg_df = df0.groupby("country").agg({
    "NY.GDP.MKTP.KN": "sum",
    "SI.DST.10TH.10": "mean",
    "SP.POP.TOTL": "sum"
}).reset_index()

agg_df["NY.GDP.MKTP.KN_x"] = pd.NA
agg_df["SI.DST.10TH.10_x"] = pd.NA
agg_df["SP.POP.TOTL_x"] = pd.NA
agg_df["NY.GDP.MKTP.KN_y"] = pd.NA
agg_df["SI.DST.10TH.10_y"] = pd.NA
agg_df["SP.POP.TOTL_y"] = pd.NA

cols_order = [
    "country",
    "NY.GDP.MKTP.KN_x", "SI.DST.10TH.10_x", "SP.POP.TOTL_x",
    "NY.GDP.MKTP.KN_y", "SI.DST.10TH.10_y", "SP.POP.TOTL_y",
    "NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"
]

result = agg_df[cols_order]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)