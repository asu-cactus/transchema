import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_64/training_0.csv", index_col=0)

grouped = df0.groupby("customer_id").agg(
    amount_x=("amount", "count"),
    amount_y=("amount", "sum"),
    avg_amount_spent=("amount", "mean")
).reset_index()

grouped["amount_x"] = grouped["amount_x"].astype(int)
grouped["amount_y"] = grouped["amount_y"].astype(float)
grouped["avg_amount_spent"] = grouped["avg_amount_spent"].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_64/target_multisource_mcts.csv", index=False)