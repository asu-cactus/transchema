import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_69/training_2.csv", index_col=0)

# Join Source4_69_0 and Source4_69_1 on user_id
join01 = pd.merge(df0, df1, on='user_id', how='inner')

# Join the result with Source4_69_2 on user_id
join012 = pd.merge(join01, df2, on='user_id', how='inner')

# Ensure correct dtypes as per target schema
join012 = join012.astype({
    'user_id': 'int64',
    'year_school': 'string',
    'floor': 'string',
    'party': 'string',
    'libcon': 'string',
    'fav_music': 'string'
})

join012.to_csv("autopipeline-benchmarks/github-pipelines/length4_69/target_multisource_mcts.csv", index=False)