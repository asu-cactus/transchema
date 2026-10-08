import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
df9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

df0_renamed = df0.rename(columns={"INBOUND_CALLS_NUM": "VISITS_NUM"})
df2_renamed = df2.rename(columns={"KEYWORDS_NUM": "VISITS_NUM"})
df3_renamed = df3.rename(columns={"INTERACTIONS_NUM": "VISITS_NUM"})
df4_renamed = df4.rename(columns={"COLLECTION_EVENTS_NUM": "VISITS_NUM"})
df9_renamed = df9.rename(columns={"TECHSUPPORT_NUM": "VISITS_NUM"})

dfs = [df0_renamed[['VISITS_NUM']], df1[['VISITS_NUM']], df2_renamed[['VISITS_NUM']], df3_renamed[['VISITS_NUM']], df4_renamed[['VISITS_NUM']], df9_renamed[['VISITS_NUM']]]

result = pd.concat(dfs, ignore_index=True)

result = result.astype({'VISITS_NUM': 'Int64'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)