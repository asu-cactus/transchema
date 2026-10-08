import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=["y"], var_name="feature", value_name="value")

df_grouped = df_unpivot.groupby(["y", "feature"], as_index=False)["value"].sum()

df_pivot = df_grouped.pivot(index="y", columns="feature", values="value").reset_index()

df_pivot = df_pivot.rename_axis(None, axis=1)

for col in df_pivot.columns:
    if col != "y":
        df_pivot[col] = df_pivot[col].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)