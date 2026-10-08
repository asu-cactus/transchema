import pandas as pd

# Load all source tables
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

# Unpivot the numeric columns from sources 0,1,3,4,7,9 to get (ROW_WID, variable, value)
def unpivot(df, value_col_name):
    id_vars = ['ROW_WID']
    value_vars = [col for col in df.columns if col != 'ROW_WID']
    return df.melt(id_vars=id_vars, value_vars=value_vars, var_name='variable', value_name=value_col_name)

up0 = unpivot(src0, 'value')
up1 = unpivot(src1, 'value')
up3 = unpivot(src3, 'value')
up4 = unpivot(src4, 'value')
up7 = unpivot(src7, 'value')
up9 = unpivot(src9, 'value')

# Concatenate all unpivoted data
unpivoted = pd.concat([up0, up1, up3, up4, up7, up9], ignore_index=True)

# Join unpivoted with src2 on ROW_WID (left join to keep all unpivoted rows)
join1 = unpivoted.merge(src2, on='ROW_WID', how='left')

# Join with src5
join2 = join1.merge(src5, on='ROW_WID', how='left', suffixes=('', '_src5'))

# Join with src6
join3 = join2.merge(src6, on='ROW_WID', how='left', suffixes=('', '_src6'))

# Join with src8
join4 = join3.merge(src8, on='ROW_WID', how='left', suffixes=('', '_src8'))

# Now join with src9 to get KEYWORDS_NUM (src9 has ROW_WID and KEYWORDS_NUM)
final_join = join4.merge(src9[['ROW_WID', 'KEYWORDS_NUM']], on='ROW_WID', how='left')

# Group by KEYWORDS_NUM and count occurrences (number of rows per KEYWORDS_NUM)
result = final_join.groupby('KEYWORDS_NUM', dropna=False).size().reset_index(name='count')

# Rename count to KEYWORDS_NUM count? But target schema is only KEYWORDS_NUM integer.
# The target examples show KEYWORDS_NUM as integer values, no count column.
# The partial plan says GROUP_BY : [KEYWORDS_NUM], so likely the target is the distinct KEYWORDS_NUM values.
# But target examples show KEYWORDS_NUM values with counts (e.g. 1949 3), so the count is the number of occurrences of that KEYWORDS_NUM.

# So the target table is KEYWORDS_NUM and count of rows per KEYWORDS_NUM.

# Rename columns accordingly
result = result.rename(columns={'count': 'KEYWORDS_NUM'})

# But this would overwrite KEYWORDS_NUM column. Instead, keep KEYWORDS_NUM and count as separate columns.
# The target schema is ['KEYWORDS_NUM': integer], so only one column.
# The target examples show KEYWORDS_NUM values with counts, so the count is the value of KEYWORDS_NUM? No, the target examples show KEYWORDS_NUM values and their counts.

# Re-examining target examples:
# KEYWORDS_NUM
# 1949             3
# 1998             1
# 3383             4
# This suggests the first column is KEYWORDS_NUM, second column is count.

# So target schema is only one column named KEYWORDS_NUM, but the examples show two columns.

# The prompt says target schema: ['KEYWORDS_NUM': integer]
# The examples show KEYWORDS_NUM values and counts, so likely the target is a frequency table of KEYWORDS_NUM values.

# So output should be two columns: KEYWORDS_NUM and count.

# We'll output two columns: KEYWORDS_NUM and COUNT

result = final_join.groupby('KEYWORDS_NUM', dropna=False).size().reset_index(name='COUNT')

# Save result to CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)