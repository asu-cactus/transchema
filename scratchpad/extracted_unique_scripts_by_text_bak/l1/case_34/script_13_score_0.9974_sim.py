import pandas as pd

source_path = "autopipeline-benchmarks/github-pipelines/length1_34/training_0.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length1_34/target_multisource_mcts.csv"

df = pd.read_csv(source_path, index_col=0)
df = df.rename(columns={"J_CALL": "V_GENE"})
df.to_csv(target_path, index=False)