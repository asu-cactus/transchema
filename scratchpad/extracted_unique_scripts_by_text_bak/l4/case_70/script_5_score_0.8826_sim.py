import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_70/training_4.csv", index_col=0)

# The partial plan suggests a join between src0 and src1 on GEO.id and Year, but schemas are identical and union is the main operation.
# Since all sources have the same schema as target, union all sources directly.

df = pd.concat([src0, src1, src2, src3, src4], ignore_index=True)

# Ensure correct dtypes:
df['GEO.id'] = df['GEO.id'].astype(str)
df['GEO.id2'] = df['GEO.id2'].astype(str)
df['GEO.display-label'] = df['GEO.display-label'].astype(str)
df['HD01_VD01'] = df['HD01_VD01'].astype(str)
df['HD02_VD01'] = df['HD02_VD01'].astype(str)
df['Year'] = df['Year'].astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_70/target_multisource_mcts.csv", index=False)