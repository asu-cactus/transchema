import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv", index_col=0)

df_all = pd.concat([df0, df1, df2, df3], ignore_index=True)

df_all['Split'] = df_all['Split'].astype(str)
df_all['Subject'] = df_all['Subject'].astype(str)

agg_df = df_all.groupby(['SubjectId', 'Split', 'Subject'], as_index=False).agg({
    'PA': 'sum',
    'AB': 'sum',
    'H': 'sum',
    'TB': 'sum',
    'BB': 'sum',
    'SF': 'sum',
    'HBP': 'sum'
})

agg_df['SubjectId'] = agg_df['SubjectId'].astype(int)

# Convert 'Split' and 'Subject' to integer if possible, else keep as is
def try_int_convert(s):
    try:
        return int(s)
    except:
        return s

agg_df['Split'] = agg_df['Split'].apply(try_int_convert)
agg_df['Subject'] = agg_df['Subject'].apply(try_int_convert)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)