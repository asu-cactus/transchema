import pandas as pd

# Load all source files
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

# Identify numeric columns with _NUM suffix from sources 0,1,3,4,7,9
# These are the columns to unpivot (except ROW_WID)
num_cols_src0 = ['COLLECTION_EVENTS_NUM']
num_cols_src1 = ['INTERACTIONS_NUM']
num_cols_src3 = ['TECHSUPPORT_NUM']
num_cols_src4 = ['VISITS_NUM']
num_cols_src7 = ['INBOUND_CALLS_NUM']
num_cols_src9 = ['KEYWORDS_NUM']

# Create a list of dataframes with ROW_WID and the numeric column renamed to a common column 'KEYWORDS_NUM'
# Actually, the target only has KEYWORDS_NUM, so we need to unpivot all these numeric columns into one column named KEYWORDS_NUM

# For each source with a single numeric column, rename that numeric column to a generic name and keep ROW_WID
df0 = src0[['ROW_WID'] + num_cols_src0].rename(columns={'COLLECTION_EVENTS_NUM': 'KEYWORDS_NUM'})
df1 = src1[['ROW_WID'] + num_cols_src1].rename(columns={'INTERACTIONS_NUM': 'KEYWORDS_NUM'})
df3 = src3[['ROW_WID'] + num_cols_src3].rename(columns={'TECHSUPPORT_NUM': 'KEYWORDS_NUM'})
df4 = src4[['ROW_WID'] + num_cols_src4].rename(columns={'VISITS_NUM': 'KEYWORDS_NUM'})
df7 = src7[['ROW_WID'] + num_cols_src7].rename(columns={'INBOUND_CALLS_NUM': 'KEYWORDS_NUM'})
df9 = src9[['ROW_WID'] + num_cols_src9]  # Already has KEYWORDS_NUM

# Concatenate all these dataframes vertically (UNPIVOT operation)
unpivoted = pd.concat([df0, df1, df3, df4, df7, df9], ignore_index=True)

# Group by KEYWORDS_NUM and count occurrences (GROUP_BY : [KEYWORDS_NUM])
result = unpivoted.groupby('KEYWORDS_NUM', as_index=False).size().rename(columns={'size': 'count'})

# The target schema only has KEYWORDS_NUM column, and target examples show values of KEYWORDS_NUM, not counts.
# The partial plan says GROUP_BY : [KEYWORDS_NUM], but target examples show only KEYWORDS_NUM values, no counts.
# So likely the target is just the distinct KEYWORDS_NUM values from all sources combined.

# So instead of counting, just get distinct KEYWORDS_NUM values from the unpivoted data.

result = unpivoted[['KEYWORDS_NUM']].drop_duplicates().reset_index(drop=True)

# Ensure KEYWORDS_NUM is integer type
result['KEYWORDS_NUM'] = result['KEYWORDS_NUM'].astype(int)

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)