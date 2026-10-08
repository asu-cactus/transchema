import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_53/training_3.csv", index_col=0)

join_cols = ['WarID', 'PolityID']
join_result = pd.merge(s2, s1, on=join_cols, how='inner', suffixes=('_s2', '_s1'))

union_0_3 = pd.concat([s0, s3], ignore_index=True)

# The join_result has columns from s2 and s1, but s2 lacks PolityName, s1 has it.
# We want to keep PolityName from s1, and all other columns from s2 plus those from s1 that are in target.
# The target columns are:
target_cols = ['PolityName', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
               'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

# Construct join_result with target columns:
# PolityName from s1 (join_result['PolityName'])
# Other columns from s2 (join_result with suffix _s2)
df_join = pd.DataFrame()
df_join['PolityName'] = join_result['PolityName']
for col in target_cols:
    if col == 'PolityName':
        continue
    if col in join_result.columns:
        df_join[col] = join_result[col]
    elif col + '_s2' in join_result.columns:
        df_join[col] = join_result[col + '_s2']
    elif col + '_s1' in join_result.columns:
        df_join[col] = join_result[col + '_s1']
    else:
        df_join[col] = pd.NA

# union_0_3 already has all target columns except PolityName may have NaNs in s3
# Ensure columns in union_0_3 match target columns and types
union_0_3 = union_0_3[target_cols]

# Concatenate join_result and union_0_3
final_df = pd.concat([df_join, union_0_3], ignore_index=True)

# Fix data types according to target schema
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay',
            'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']

for col in int_cols:
    final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).astype(int)

final_df['PolityName'] = final_df['PolityName'].astype(str)

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_53/target_multisource_mcts.csv", index=False)