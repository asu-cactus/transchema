import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

union_result = pd.concat([source2, source2], ignore_index=True)

join_result = pd.merge(union_result, source1, how='inner', left_on='Country', right_on='Country')

joined_all = pd.merge(join_result, source0, how='inner', left_on='Country', right_on='Country Name')

result = joined_all[['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita', '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)