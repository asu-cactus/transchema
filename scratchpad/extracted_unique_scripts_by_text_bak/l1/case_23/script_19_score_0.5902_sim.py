import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_23/training_0.csv", index_col=0)
df_unpivoted = df0.melt(id_vars=["customer_id"], value_vars=["amount", "date"], var_name="variable", value_name="value")
df_result = df_unpivoted[df_unpivoted["variable"] == "amount"][["customer_id", "value"]]
df_result = df_result.rename(columns={"value": "amount"})
df_result["customer_id"] = df_result["customer_id"].astype(int)
df_result["amount"] = df_result["amount"].astype(float)
df_result.to_csv("autopipeline-benchmarks/github-pipelines/length1_23/target_multisource_mcts.csv", index=False)