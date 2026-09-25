import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length2_64/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length2_64/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length2_64/target_multisource_mcts.csv"

source0 = pd.read_csv(source0_path, index_col=0)
source1 = pd.read_csv(source1_path, index_col=0)

grouped_1 = source1.groupby(['Timepoint', 'Mouse ID'], as_index=False).agg({
    'Tumor Volume (mm3)': 'mean',
    'Metastatic Sites': 'mean'
})

merged = pd.merge(grouped_1, source0, on='Mouse ID', how='inner')

result = merged[['Drug', 'Timepoint', 'Mouse ID']]

result.to_csv(target_path, index=False)