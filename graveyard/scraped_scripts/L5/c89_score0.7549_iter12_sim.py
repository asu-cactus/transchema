import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_89/training_4.csv", index_col=0)

agg_count = src4['Ord_id'].count()
agg_avg = src4['Profit'].mean()
agg_min = src4['Profit'].min()
agg_max = src4['Profit'].max()

result = pd.DataFrame({
    'Profit': [agg_avg, agg_min, agg_max]
}, index=[2, 0, 1])

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_89/target_multisource_mcts.csv")