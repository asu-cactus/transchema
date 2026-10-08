import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_52/training_3.csv", index_col=0)

join_0 = pd.merge(s1, s2, on="zipcode", suffixes=('_x', '_y'))
join_1 = pd.merge(join_0, s0, on="zipcode")
join_2 = pd.merge(join_1, s3, on="zipcode", suffixes=('_x_5', '_y_7'))

result = pd.DataFrame()
result['zipcode'] = join_2['zipcode']
result['businesses_x'] = join_2['businesses_x']
result['counts_x'] = join_2['counts_x']
result['businesses_y'] = join_2['businesses_y']
result['counts_y'] = join_2['counts_y']
result['businesses_x_5'] = join_2['businesses']
result['counts_x_6'] = join_2['counts']
result['businesses_y_7'] = join_2['businesses_y_7']
result['counts_y_8'] = join_2['counts_y_8'] = join_2['counts']

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_52/target_multisource_mcts.csv", index=False)