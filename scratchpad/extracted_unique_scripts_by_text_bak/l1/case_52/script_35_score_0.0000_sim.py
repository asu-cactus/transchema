import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length1_52/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

pivoted = df.pivot_table(index='condition', columns='click', aggfunc='size', fill_value=0)
pivoted.columns = pivoted.columns.astype(str)
pivoted = pivoted.reset_index()

pivoted = pivoted.rename(columns={'0': '0'})
pivoted['condition'] = pivoted['condition'].astype(int)
pivoted['0'] = pivoted.get('0', 0).astype(int)

pivoted[['condition', '0']].to_csv("autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv", index=False)