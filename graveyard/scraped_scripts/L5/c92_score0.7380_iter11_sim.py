import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_92/training_0.csv", index_col=0)

df_union = pd.concat([df0], ignore_index=True)

df_unpivot = df_union.melt(id_vars=["country", "year"], value_vars=["NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"], var_name="variable", value_name="value")

df_pivot_x = df_unpivot[df_unpivot["year"] == df_unpivot["year"].min()].pivot(index="country", columns="variable", values="value")
df_pivot_x.columns = [col + "_x" for col in df_pivot_x.columns]

df_pivot_y = df_unpivot[df_unpivot["year"] == df_unpivot["year"].max()].pivot(index="country", columns="variable", values="value")
df_pivot_y.columns = [col + "_y" for col in df_pivot_y.columns]

df_pivot = df_union.pivot(index="country", columns="year", values=["NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"])
df_pivot.columns = [f"{var}" for var in df_pivot.columns.get_level_values(0)]

df_target = df_pivot_x.join(df_pivot_y, how="outer").join(df_pivot, how="outer").reset_index()

df_target = df_target[["country",
                       "NY.GDP.MKTP.KN_x", "SI.DST.10TH.10_x", "SP.POP.TOTL_x",
                       "NY.GDP.MKTP.KN_y", "SI.DST.10TH.10_y", "SP.POP.TOTL_y",
                       "NY.GDP.MKTP.KN", "SI.DST.10TH.10", "SP.POP.TOTL"]]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length5_92/target_multisource_mcts.csv", index=False)