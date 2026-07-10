import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_7/training_3.csv", index_col=0)

joined = pd.merge(src2, src1, left_on="COD_AREANEGO", right_on="cod_areanego", how="inner")

grouped = joined.groupby("des_zona", dropna=False).agg(
    COD_PERSONA_x=pd.NamedAgg(column="COD_PERSONA", aggfunc="max"),
    COD_AREANEGO=pd.NamedAgg(column="COD_AREANEGO", aggfunc="max"),
).reset_index()

grouped["COD_PERSONA_x"] = grouped["COD_PERSONA_x"].astype("Int64")
grouped["COD_AREANEGO"] = grouped["COD_AREANEGO"].astype("Int64")
grouped["des_zona"] = grouped["des_zona"].astype(str)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_7/target_multisource_mcts.csv", index=False)