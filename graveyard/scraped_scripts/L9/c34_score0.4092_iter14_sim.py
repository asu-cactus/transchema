import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

num_dfs = [src0, src1, src3, src4, src7, src9]
num_cols = ['COLLECTION_EVENTS_NUM', 'INTERACTIONS_NUM', 'TECHSUPPORT_NUM', 'VISITS_NUM', 'INBOUND_CALLS_NUM', 'KEYWORDS_NUM']

for df, col in zip(num_dfs, num_cols):
    df.rename(columns={col: 'VALUE'}, inplace=True)
    df['METRIC'] = col

num_all = pd.concat(num_dfs, ignore_index=True)

unpivoted = num_all[['ROW_WID', 'METRIC', 'VALUE']]

grouped = unpivoted.groupby('VALUE', dropna=False).size().reset_index(name='KEYWORDS_NUM')

grouped = grouped.rename(columns={'VALUE': 'KEYWORDS_NUM'})

grouped['KEYWORDS_NUM'] = grouped['KEYWORDS_NUM'].astype(int)

grouped[['KEYWORDS_NUM']].to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)