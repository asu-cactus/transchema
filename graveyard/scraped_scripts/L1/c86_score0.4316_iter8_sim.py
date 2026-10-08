import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_86/training_0.csv", index_col=0)

union_df = pd.concat([df0, df1], ignore_index=True)
project_df = union_df[['neighbourhood', 'price']]
rename_df = project_df.rename(columns={'price': 'price_24'})
rename_df['price_24'] = rename_df['price_24'].astype(int)

rename_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_86/target_multisource_mcts.csv", index=False)