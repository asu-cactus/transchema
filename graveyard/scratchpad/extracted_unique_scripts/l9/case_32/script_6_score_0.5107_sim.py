import pandas as pd

# Load all source tables
src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
src3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
src4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
src5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
src6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
src7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
src8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
src9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# Unpivot step: convert all numeric *_NUM columns from src0, src1, src2, src3, src4, src9 into a single long table keyed by ROW_WID
# Extract numeric columns except ROW_WID from each source and rename the numeric column to a common name 'VISITS_NUM' for union
def unpivot_single(df, value_col):
    return df.rename(columns={value_col: 'VISITS_NUM'})[['ROW_WID', 'VISITS_NUM']]

up0 = unpivot_single(src0, 'INBOUND_CALLS_NUM')
up1 = unpivot_single(src1, 'VISITS_NUM')
up2 = unpivot_single(src2, 'KEYWORDS_NUM')
up3 = unpivot_single(src3, 'INTERACTIONS_NUM')
up4 = unpivot_single(src4, 'COLLECTION_EVENTS_NUM')
up9 = unpivot_single(src9, 'TECHSUPPORT_NUM')

unpivot_result = pd.concat([up0, up1, up2, up3, up4, up9], ignore_index=True)

# Join unpivot_result with src5, src6, src7, src8 on ROW_WID sequentially
join_result = unpivot_result.merge(src5, on='ROW_WID', how='left')
join_result = join_result.merge(src6, on='ROW_WID', how='left', suffixes=('', '_6'))
join_result = join_result.merge(src7, on='ROW_WID', how='left', suffixes=('', '_7'))
join_result = join_result.merge(src8, on='ROW_WID', how='left', suffixes=('', '_8'))

# Group by VISITS_NUM as per partial plan
# The target schema is only VISITS_NUM (integer), and target examples show counts of VISITS_NUM values
# So we group by VISITS_NUM and count occurrences
result = join_result.groupby('VISITS_NUM', dropna=False).size().reset_index(name='count')

# The target schema only has VISITS_NUM column, so we keep only VISITS_NUM column
# The target examples show VISITS_NUM as integer, so convert to int if possible
result['VISITS_NUM'] = result['VISITS_NUM'].astype('Int64')  # nullable integer type to keep NaNs if any

# Save the result with only VISITS_NUM column (dropping count column as target schema has only VISITS_NUM)
# But since target examples show counts of VISITS_NUM values, likely the target table is the grouped counts by VISITS_NUM
# The prompt target schema is ['VISITS_NUM': integer] only, no count column
# So we output the grouped VISITS_NUM values (unique VISITS_NUM values)
# But the example target shows counts of VISITS_NUM values (e.g. 3141 rows with VISITS_NUM=5)
# So the target table is the grouped counts by VISITS_NUM, but only VISITS_NUM column is shown in schema
# This is ambiguous, but since the partial plan says GROUP_BY : [VISITS_NUM], we output the grouped counts as rows with VISITS_NUM repeated count times

# Expand rows by count to match target examples count
result_expanded = result.loc[result.index.repeat(result['count'])].reset_index(drop=True)
result_expanded = result_expanded[['VISITS_NUM']]

result_expanded.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)