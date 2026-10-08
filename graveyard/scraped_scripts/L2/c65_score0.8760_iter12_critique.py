import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_65/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_65/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_65/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

# Join on 'fname' only, left join to keep all rows from df0
joined = pd.merge(df0, df1, how='left', left_on='fname', right_on='fname')

# Count number of rows in df1 per fname; count non-null 'Slice n°' as indicator of matching rows
result = joined.groupby('fname')['Slice n°'].count().reset_index(name='row_count')

result.to_csv(target_path, index=False)