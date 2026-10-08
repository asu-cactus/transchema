import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

df_unpivot = df.melt(id_vars=["country", "year"], value_vars=["NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"], var_name="variable", value_name="value")

df_x = df_unpivot.rename(columns={"value": "value_x"})
df_y = df_unpivot.rename(columns={"value": "value_y"})

df_joined = pd.merge(df_x, df_y, on=["country", "year", "variable"], how="outer", suffixes=("_x", "_y"))

df_pivot_x = df_joined.pivot_table(index=["country", "year"], columns="variable", values="value_x").reset_index()
df_pivot_y = df_joined.pivot_table(index=["country", "year"], columns="variable", values="value_y").reset_index()

df_pivot_x.columns = ["country", "year"] + [col + "_x" for col in df_pivot_x.columns if col not in ["country", "year"]]
df_pivot_y.columns = ["country", "year"] + [col + "_y" for col in df_pivot_y.columns if col not in ["country", "year"]]

df_merged = pd.merge(df_pivot_x, df_pivot_y, on=["country", "year"], how="outer")

df_original = df[["country", "NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"]]

df_final = pd.merge(df_merged, df_original, on="country", how="outer")

df_final = df_final[[
    "country",
    "NY.GDP.MKTP.KN_x",
    "SI.DST.10TH.10_x",
    "SP.POP.TOTL_x",
    "NY.GDP.MKTP.KN_y",
    "SI.DST.10TH.10_y",
    "SP.POP.TOTL_y",
    "NY.GDP.MKTP.KN",
    "SI.DST.10TH.10",
    "SP.POP.TOTL"
]]

df_final.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)