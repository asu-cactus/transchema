import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_10/training_0.csv", index_col=0)

df_long = df.melt(id_vars=["PRECINCT"], value_vars=["ELIGIBLE_VOTERS", "POLLS", "EARLY_VOING", "ABSENTEE", "PROVISIONAL"], var_name="variable", value_name="value")

df_grouped = df_long.groupby(["PRECINCT", "variable"], as_index=False)["value"].sum()

df_pivot = df_grouped.pivot(index="PRECINCT", columns="variable", values="value").reset_index()

df_pivot.columns.name = None

df_pivot["ELIGIBLE_VOTERS"] = df_pivot["ELIGIBLE_VOTERS"].astype(int)
df_pivot["POLLS"] = df_pivot["POLLS"].astype(int)
df_pivot["EARLY_VOING"] = df_pivot["EARLY_VOING"].astype(int)
df_pivot["ABSENTEE"] = df_pivot["ABSENTEE"].astype(int)
df_pivot["PROVISIONAL"] = df_pivot["PROVISIONAL"].astype(int)

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_10/target_multisource_mcts.csv", index=False)