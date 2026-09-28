import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_53/training_0.csv", index_col=0)

joined = pd.merge(source0, source0, on="Purchase ID", suffixes=("", "_y"))

df = pd.DataFrame()
df["Age Category"] = joined["Age"].astype(int)
df["Purchase ID"] = joined["Purchase ID"].astype(int)
df["SN"] = joined["SN"].astype(int, errors='ignore') if joined["SN"].dtype != int else joined["SN"].astype(int)
df["Purchase Count"] = joined.groupby("Purchase ID")["Purchase ID"].transform("count").astype(int)
df["Gender"] = joined["Gender"].map({"Male": 1, "Female": 2}).fillna(0).astype(int)
df["Item ID"] = joined["Item ID"].astype(int)
df["Item Name"] = joined["Item Name"].astype('category').cat.codes.astype(int)
df["Price"] = joined["Price"].astype(int)
df["Total Purchase Value"] = joined.groupby("Purchase ID")["Price"].transform("sum").astype(float)
df["Average Purchase Price"] = joined.groupby("Purchase ID")["Price"].transform("mean").astype(float)

df = df.drop_duplicates(subset=["Age Category", "Purchase ID", "SN", "Purchase Count", "Gender", "Item ID", "Item Name", "Price", "Total Purchase Value", "Average Purchase Price"])

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_53/target_multisource_mcts.csv", index=False)