import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_47/training_3.csv", index_col=0)

agg = s1.groupby("IsIntervention").agg(
    WarID=("WarID", "count"),
    WarShortName=("WarShortName", pd.Series.nunique),
    WarType=("WarType", pd.Series.nunique),
).reset_index()

result = pd.merge(agg, s3[["IsInternational", "WarID"]], left_on="IsIntervention", right_on="WarID", how="left")

result = result.drop(columns=["WarID_y"]).rename(columns={"WarID_x": "WarID"})

result = result[["IsIntervention", "WarID", "WarShortName", "WarType", "IsInternational"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_47/target_multisource_mcts.csv", index=False)