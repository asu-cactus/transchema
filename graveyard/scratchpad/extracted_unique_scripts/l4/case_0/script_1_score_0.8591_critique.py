import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)

# Join src0 and src2 on COD_PERSONA
join_0_2 = pd.merge(src0, src2, on="COD_PERSONA", how="inner")

# Join the above result with src1 on COD_IDCONTRA
join_0_2_1 = pd.merge(join_0_2, src1, on="COD_IDCONTRA", how="inner")

# Join the above result with src3 on src0.COD_OFICIPAL = src3.COD_OFICI
final_join = pd.merge(join_0_2_1, src3, left_on="COD_OFICIPAL", right_on="COD_OFICI", how="inner")

# Group by des_territ to get unique territory descriptions
result = final_join.groupby("des_territ", dropna=False).size().reset_index(name="count")

# Select only des_territ column as per target schema
output = result[["des_territ"]]

output.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)