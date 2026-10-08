import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_50/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_50/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length2_50/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

grouped_source0 = df0.groupby('sex').agg({'age':'mean'}).reset_index()  # age mean just to keep a numeric column, will drop later
# Actually, target schema is sex, G1, G2, G3. We need to join on sex, but source1 has no sex column, only ID, G1, G2, G3.
# So we need to join source1 with source0 on ID to get sex for each ID, then group by sex and average G1,G2,G3.

# Join source1 with source0 on ID to get sex for each record in source1
df1_with_sex = df1.merge(df0[['sex']], left_index=True, right_index=True, how='left')

# Group by sex and average G1, G2, G3
result = df1_with_sex.groupby('sex')[['G1','G2','G3']].mean().reset_index()

result.to_csv(output_path, index=False)