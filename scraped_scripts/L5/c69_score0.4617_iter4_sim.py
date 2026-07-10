import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_3.csv", index_col=0)
source4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_69/training_4.csv", index_col=0)

df = pd.merge(source3, source0, on="Prod_id", how="inner")
df = pd.merge(df, source1, on="Ord_id", how="inner")
df = pd.merge(df, source2, on="Cust_id", how="inner")
df = pd.merge(df, source4, on="Ship_id", how="inner")

result = df[["Ship_Date", "Ord_id", "Prod_id", "Ship_id", "Cust_id"]].copy()

def to_int_id(x):
    if isinstance(x, str):
        return int(x.split('_')[-1])
    return x

result["Ord_id"] = result["Ord_id"].map(to_int_id)
result["Prod_id"] = result["Prod_id"].map(to_int_id)
result["Ship_id"] = result["Ship_id"].map(to_int_id)
result["Cust_id"] = result["Cust_id"].map(to_int_id)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_69/target_multisource_mcts.csv", index=False)