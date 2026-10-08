import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_38/training_0.csv", index_col=0)

melted_sad = df0.melt(id_vars=["user_id"], value_vars=["sad.depressed"], var_name="mood", value_name="sad")
melted_stressed = df0.melt(id_vars=["user_id"], value_vars=["open.stressed"], var_name="mood", value_name="stressed")

result = pd.merge(melted_sad[["user_id", "sad"]], melted_stressed[["user_id", "stressed"]], on="user_id")

result["sad"] = result["sad"].astype(float)
result["stressed"] = result["stressed"].astype(float)
result = result[["user_id", "sad", "stressed"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_38/target_multisource_mcts.csv", index=False)