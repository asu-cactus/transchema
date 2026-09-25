import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, on="user_id", suffixes=('_left', '_right'))

df_pivot = df_joined.melt(id_vars=["user_id", "time_left"], value_vars=["bet_left", "win_left", "bet_right", "win_right"], var_name="variable", value_name="value")

df_pivot["time"] = df_pivot["time_left"]
df_pivot["variable"] = df_pivot["variable"].str.replace(r'_(left|right)$', '', regex=True)

df_result = df_pivot.pivot_table(index=["user_id", "time"], columns="variable", values="value", aggfunc='first').reset_index()

df_result = df_result.astype({"user_id": str, "time": str, "bet": float, "win": float})

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)