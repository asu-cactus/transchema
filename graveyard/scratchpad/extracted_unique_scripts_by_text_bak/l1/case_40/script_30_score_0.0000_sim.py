import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_40/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_40/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

union_df = pd.concat(dfs, ignore_index=True)

result = union_df[['CUSTOMERNAME', 'ORDERNUMBER', 'QUANTITYORDERED']].copy()

result['ORDERNUMBER'] = pd.to_numeric(result['ORDERNUMBER'], errors='coerce').astype('Int64')
result['QUANTITYORDERED'] = pd.to_numeric(result['QUANTITYORDERED'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_40/target_multisource_mcts.csv", index=False)