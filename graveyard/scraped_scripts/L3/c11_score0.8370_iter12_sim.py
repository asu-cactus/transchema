import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="SN")

unpivoted = joined.melt(id_vars=["SN", "Price_x"], value_vars=["Price_y"], var_name="variable", value_name="Price")

grouped = unpivoted.groupby(["SN", "Price"]).size().reset_index(name="count")

grouped["SN"] = grouped["SN"].astype(str)
grouped["Price"] = grouped["Price"].astype(float)
grouped["count"] = grouped["count"].astype(int)

grouped.rename(columns={"Price": "Price"}, inplace=True)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)