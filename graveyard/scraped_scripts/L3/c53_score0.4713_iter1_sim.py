import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df[['B-day', 'ID Number', 'Name', 'Fed', 'Sex']]

df = df.rename(columns={'Name': 'Name_x', 'Fed': 'Fed_x', 'Sex': 'Sex_x'})

df.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)