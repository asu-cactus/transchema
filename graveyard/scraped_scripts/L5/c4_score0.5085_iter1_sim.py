import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_2.csv", index_col=0)
source3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_4/training_3.csv", index_col=0)

source0['Year Inducted'] = pd.to_numeric(source0['Year Inducted'], errors='coerce')
source2['Year Inducted'] = pd.to_numeric(source2['Year Inducted'], errors='coerce')
source0['Years Waited'] = pd.to_numeric(source0['Years Waited'], errors='coerce').astype('Int64')
source2['Years Waited'] = pd.to_numeric(source2['Years Waited'], errors='coerce').astype('Int64')
source0['# of Years Nominated'] = pd.to_numeric(source0['# of Years Nominated'], errors='coerce').astype('Int64')
source2['# of Years Nominated'] = pd.to_numeric(source2['# of Years Nominated'], errors='coerce').astype('Int64')

union_result = pd.concat([source0, source2], ignore_index=True, sort=False)

join_result_1 = pd.merge(union_result, source1, on='Artist', how='left')

source3['Certified Units (Millions)'] = pd.to_numeric(source3['Certified Units (Millions)'], errors='coerce')
join_result_2 = pd.merge(join_result_1, source3, on='Artist', how='left')

final = join_result_2[['Artist', 'Year Inducted', 'Years Waited', '# of Years Nominated', 'Inducted By', 'Influenced', 'Certified Units (Millions)']]

final['Year Inducted'] = final['Year Inducted'].astype(float)
final['Years Waited'] = final['Years Waited'].astype('Int64')
final['# of Years Nominated'] = final['# of Years Nominated'].astype('Int64')
final['Influenced'] = final['Influenced'].astype('Int64')
final['Certified Units (Millions)'] = final['Certified Units (Millions)'].astype(float)

final.to_csv("autopipeline-benchmarks/github-pipelines/length5_4/target_multisource_mcts.csv", index=False)