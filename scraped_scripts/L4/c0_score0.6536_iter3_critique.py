import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

# Start from s3 (dimension table) and left join s0 on office code
j1 = pd.merge(s3, s0, left_on="COD_OFICI", right_on="COD_OFICIPAL", how="left")

# Left join s1 on COD_PERSONA
j2 = pd.merge(j1, s1, on="COD_PERSONA", how="left")

# Left join s2 on COD_PERSONA
j3 = pd.merge(j2, s2, on="COD_PERSONA", how="left")

# Group by des_territ to get unique territories
result = j3[["des_territ"]].drop_duplicates().reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)