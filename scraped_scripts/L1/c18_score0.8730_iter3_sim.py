import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_18/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=["y"], var_name="variable", value_name="value")

df_grouped = df_unpivot.groupby(["y", "variable"], as_index=False)["value"].sum()

df_pivot = df_grouped.pivot(index="y", columns="variable", values="value").reset_index()

df_pivot.columns.name = None

for col in df_pivot.columns:
    if col != "y":
        df_pivot[col] = df_pivot[col].round().astype(int)

df_pivot = df_pivot[["y", "sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]]

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_18/target_multisource_mcts.csv", index=False)