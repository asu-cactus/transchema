import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_21/training_0.csv", index_col=0)
df_agg = df0.groupby("Country", as_index=False).agg(AverageTemperature_x=("AverageTemperature", "mean"))
df_agg = df_agg.rename(columns={"AverageTemperature_x": "AverageTemperature_x"})

# Since only one source is given, and target requires two temperature columns,
# but only one source is provided, we assume the second temperature column is missing.
# The target schema requires AverageTemperature_x and AverageTemperature_y.
# The partial plan and source info only mention one source.
# So we create AverageTemperature_y as NaN to match target schema.

df_agg["AverageTemperature_y"] = pd.NA

df_agg = df_agg[["Country", "AverageTemperature_x", "AverageTemperature_y"]]

df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_21/target_multisource_mcts.csv", index=False)