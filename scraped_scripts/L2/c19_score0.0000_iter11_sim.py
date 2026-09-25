import pandas as pd

src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_19/training_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_19/training_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_19/training_2.csv', index_col=0)

df = pd.concat([src0, src1, src2], ignore_index=True)

df = df[['Dates', 'Action']]

df['Dates'] = pd.to_datetime(df['Dates'], errors='coerce')
df = df.dropna(subset=['Dates'])
df['Dates'] = df['Dates'].dt.strftime('%Y%m%d').astype(int)

df['Action'] = pd.to_numeric(df['Action'], errors='coerce')
df = df.dropna(subset=['Action'])
df['Action'] = df['Action'].astype(int)

df.to_csv('autopipeline-benchmarks/github-pipelines/length2_19/target_multisource_mcts.csv', index=False)