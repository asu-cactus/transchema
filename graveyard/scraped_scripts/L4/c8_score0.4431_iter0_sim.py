import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_8/training_1.csv", index_col=0)

df_join = pd.merge(df0, df1, left_on=["COD_AREANEGO", "COD_PERSONA"], right_on=["cod_areanego", "COD_OFICI"], how="inner")

result = df_join.groupby("des_zona", as_index=False).agg(COD_PERSONA_x=("COD_PERSONA", "count"), COD_AREANEGO=("COD_AREANEGO", "first"))

result["COD_PERSONA_x"] = result["COD_PERSONA_x"].astype(int)
result["COD_AREANEGO"] = result["COD_AREANEGO"].astype(int)
result["des_zona"] = result["des_zona"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_8/target_multisource_mcts.csv", index=False)