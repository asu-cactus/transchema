import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_33/training_9.csv", index_col=0)

# UNPIVOT step: melt numeric *_NUM columns from s0,s1,s2,s3,s6,s8 into long format with ROW_WID and INTERACTIONS_NUM
def unpivot_num(df):
    id_col = 'ROW_WID'
    val_cols = [c for c in df.columns if c.endswith('_NUM') and c != 'INTERACTIONS_NUM']
    melted = df.melt(id_vars=[id_col], value_vars=val_cols, var_name='metric', value_name='INTERACTIONS_NUM')
    return melted[[id_col, 'INTERACTIONS_NUM']]

u0 = unpivot_num(s0)
u1 = unpivot_num(s1)
u2 = unpivot_num(s2)
u3 = unpivot_num(s3)
u6 = unpivot_num(s6)
# s8 already has INTERACTIONS_NUM column, just select ROW_WID and INTERACTIONS_NUM
u8 = s8[['ROW_WID', 'INTERACTIONS_NUM']]

unpivoted = pd.concat([u0, u1, u2, u3, u6, u8], ignore_index=True)

# UNION step: union s4,s5,s7,s9 (all have same schema)
unioned = pd.concat([s4, s5, s7, s9], ignore_index=True)

# JOIN step: join unioned with unpivoted on ROW_WID
joined = pd.merge(unioned, unpivoted, on='ROW_WID', how='inner')

# PROJECT step: select only INTERACTIONS_NUM column as target schema
result = joined[['INTERACTIONS_NUM']]

# Save result
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_33/target_multisource_mcts.csv", index=False)