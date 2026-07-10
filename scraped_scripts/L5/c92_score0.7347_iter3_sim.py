import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

agg_x = df0.groupby("country").agg({
    "NY.GDP.MKTP.KN": "sum",
    "SI.DST.10TH.10": "mean",
    "SP.POP.TOTL": "sum"
}).reset_index()
agg_x.columns = ["country", "NY.GDP.MKTP.KN_x", "SI.DST.10TH.10_x", "SP.POP.TOTL_x"]

agg_y = df0.groupby("country").agg({
    "NY.GDP.MKTP.KN": "sum",
    "SI.DST.10TH.10": "mean",
    "SP.POP.TOTL": "sum"
}).reset_index()
agg_y.columns = ["country", "NY.GDP.MKTP.KN_y", "SI.DST.10TH.10_y", "SP.POP.TOTL_y"]

merged = pd.merge(agg_x, agg_y, on="country", how="outer")

merged["NY.GDP.MKTP.KN"] = merged["NY.GDP.MKTP.KN_x"]
merged["SI.DST.10TH.10"] = merged["SI.DST.10TH.10_x"]
merged["SP.POP.TOTL"] = merged["SP.POP.TOTL_x"]

result = merged[[
    "country",
    "NY.GDP.MKTP.KN_x", "SI.DST.10TH.10_x", "SP.POP.TOTL_x",
    "NY.GDP.MKTP.KN_y", "SI.DST.10TH.10_y", "SP.POP.TOTL_y",
    "NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"
]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)