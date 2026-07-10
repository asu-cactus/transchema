import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

union_result = pd.concat([source1, source2.rename(columns={'school': 'name'})], ignore_index=True)

merged = pd.merge(union_result, source0, left_on='name', right_on='school', how='left')

result = merged[['School ID', 'name', 'type', 'size', 'budget',
                 'Average Math Score', 'Average Reading Score',
                 'Number Passing Math', 'Number Passing Reading']]

result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Number Passing Math'] = result['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = result['Number Passing Reading'].astype('Int64')
result['Average Math Score'] = result['Average Math Score'].astype(float)
result['Average Reading Score'] = result['Average Reading Score'].astype(float)
result['type'] = result['type'].astype(str)
result['name'] = result['name'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)