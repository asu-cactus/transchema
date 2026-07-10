import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_78/training_0.csv", index_col=0)

df_unpivot = df0.melt(id_vars=["Product"], value_vars=["Quantity", "Price"], var_name="Measure", value_name="Value")
df_price = df_unpivot[df_unpivot["Measure"] == "Price"][["Product", "Value"]]
df_price = df_price.rename(columns={"Value": "Price"})
df_price["Price"] = df_price["Price"].astype(float)

df_price.to_csv("autopipeline-benchmarks/github-pipelines/length1_78/target_multisource_mcts.csv", index=False)