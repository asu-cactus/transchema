import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_39/training_1.csv", index_col=0)

agg = source1.groupby('Mouse ID').agg({'Metastatic Sites':'sum', 'Timepoint':['min','max']})
agg.columns = ['Metastatic Sites Sum', 'Timepoint Min', 'Timepoint Max']
agg = agg.reset_index()

merged = pd.merge(source0, agg, on='Mouse ID', how='inner')

merged['Timepoint'] = merged[['Timepoint Min', 'Timepoint Max']].max(axis=1)

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result['Timepoint'] = result['Timepoint'].astype(int)
result['Mouse ID'] = result['Mouse ID'].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_39/target_multisource_mcts.csv", index=False)