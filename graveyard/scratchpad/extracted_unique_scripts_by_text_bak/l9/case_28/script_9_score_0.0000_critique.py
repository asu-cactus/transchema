import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

# Join the four tables with same schema on ROW_WID
join_1 = pd.merge(s3, s5, on="ROW_WID", how="inner", suffixes=('_3', '_5'))
join_2 = pd.merge(join_1, s6, on="ROW_WID", how="inner")
join_2 = join_2.rename(columns={"ARPU": "ARPU_6"})
join_3 = pd.merge(join_2, s7, on="ROW_WID", how="inner")
join_3 = join_3.rename(columns={"ARPU": "ARPU_7"})

# Join all other tables on ROW_WID
join_4 = pd.merge(join_3, s0, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s1, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s2, on="ROW_WID", how="inner")
join_7 = pd.merge(join_6, s4, on="ROW_WID", how="inner")
join_8 = pd.merge(join_7, s8, on="ROW_WID", how="inner")
join_9 = pd.merge(join_8, s9, on="ROW_WID", how="inner")

# Now, ARPU columns from s3, s5, s6, s7 are ARPU_3, ARPU_5, ARPU_6, ARPU_7
# They should be identical or close; take mean of these ARPU columns per ROW_WID
arpu_cols = ['ARPU_3', 'ARPU', 'ARPU_6', 'ARPU_7']
# Note: s5's ARPU column was renamed to 'ARPU' after merge with s3 and s5 (suffixes used only once)
# Actually, after first merge s3 and s5, s3.ARPU is 'ARPU' and s5.ARPU is 'ARPU_5'
# So fix suffixes to keep all ARPU columns distinct

# Re-merge with proper suffixes to keep all ARPU columns distinct
join_1 = pd.merge(s3, s5, on="ROW_WID", how="inner", suffixes=('_3', '_5'))
join_2 = pd.merge(join_1, s6, on="ROW_WID", how="inner", suffixes=('', '_6'))
join_2 = join_2.rename(columns={"ARPU": "ARPU_6"})
join_3 = pd.merge(join_2, s7, on="ROW_WID", how="inner", suffixes=('', '_7'))
join_3 = join_3.rename(columns={"ARPU": "ARPU_7"})

# Join all other tables on ROW_WID
join_4 = pd.merge(join_3, s0, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s1, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s2, on="ROW_WID", how="inner")
join_7 = pd.merge(join_6, s4, on="ROW_WID", how="inner")
join_8 = pd.merge(join_7, s8, on="ROW_WID", how="inner")
join_9 = pd.merge(join_8, s9, on="ROW_WID", how="inner")

# Compute mean ARPU across the 4 ARPU columns
join_9['ARPU_mean'] = join_9[['ARPU_3', 'ARPU_5', 'ARPU_6', 'ARPU_7']].mean(axis=1)

# Group by ROW_WID and aggregate ARPU_mean by mean to remove duplicates if any
result = join_9.groupby('ROW_WID', as_index=False).agg({'ARPU_mean': 'mean'})

# Rename column to ARPU as per target schema
result = result.rename(columns={'ARPU_mean': 'ARPU'})

# Output only ARPU column
result[['ARPU']].to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)