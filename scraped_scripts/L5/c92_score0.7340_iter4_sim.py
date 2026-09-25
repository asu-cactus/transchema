import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

df0_long = df0.melt(id_vars=["country", "year"], value_vars=["NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"],
                    var_name="indicator", value_name="value")

df_x = df0_long[df0_long["year"] == df0["year"].min()]
df_x = df_x.pivot(index="country", columns="indicator", values="value").add_suffix("_x").reset_index()

df_y = df0_long[df0_long["year"] == df0["year"].max()]
df_y = df_y.pivot(index="country", columns="indicator", values="value").add_suffix("_y").reset_index()

df_latest = df0_long[df0_long["year"] == df0["year"].max()]
df_latest = df_latest.pivot(index="country", columns="indicator", values="value").reset_index()

df = df_x.merge(df_y, on="country", how="outer").merge(df_latest, on="country", how="outer")

df.columns.name = None

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)