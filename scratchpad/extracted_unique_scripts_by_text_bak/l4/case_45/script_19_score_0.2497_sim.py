import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_45/training_3.csv", index_col=0)

union_0_1 = pd.concat([s0, s1], ignore_index=True)

join_1 = pd.merge(union_0_1, s2, on="WarID", how="outer", suffixes=('', '_s2'))
join_2 = pd.merge(join_1, s3, on="WarID", how="outer", suffixes=('', '_s3'))

result = join_2[["WarType", "WarID", "WarShortName", "IsInternational", "IsIntervention"]]

result["WarType"] = result["WarType"].astype("Int64")
result["WarID"] = result["WarID"].astype("Int64")
result["WarShortName"] = result["WarShortName"].astype("Int64", errors='ignore')
if result["WarShortName"].dtype == object:
    # Convert WarShortName to integer if possible, else keep as is
    try:
        result["WarShortName"] = result["WarShortName"].astype("Int64")
    except:
        pass
result["IsInternational"] = result["IsInternational"].fillna(0).astype("Int64")
result["IsIntervention"] = result["IsIntervention"].fillna(0).astype("Int64")

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts.csv", index=False)