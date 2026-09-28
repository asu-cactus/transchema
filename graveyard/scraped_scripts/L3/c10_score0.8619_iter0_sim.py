import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_10/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_10/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_10/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

grouped_source0 = source0.groupby('Postalcode', as_index=False).agg({
    'Borough': 'first',
    'Neighborhood': lambda x: ', '.join(sorted(set(n.strip() for v in x for n in v.split(','))))
})

merged = pd.merge(grouped_source0, source1, on='Postalcode', how='inner')

merged['Neighborhood_joined'] = merged['Neighborhood']

merged = merged[['Postalcode', 'Latitude', 'Longitude', 'Borough', 'Neighborhood', 'Neighborhood_joined']]

merged.to_csv(target_path, index=False)