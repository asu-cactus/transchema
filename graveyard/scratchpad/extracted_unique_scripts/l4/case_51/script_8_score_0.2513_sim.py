import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_51/training_3.csv", index_col=0)

join_cols = ['WarID', 'PolityID', 'Side']
join_result = pd.merge(s1, s0, on=join_cols, suffixes=('_join', '_union'))

union_cols = ['WarID', 'PolityID', 'PolityName', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'Side', 'IsInitiator', 'Outcome', 'Deaths']
s2_sel = s2[union_cols]
s3_sel = s3[union_cols]
union_result = pd.concat([s2_sel, s3_sel], ignore_index=True)

# Prepare join_result columns to match target schema:
# Use columns from s0 (union suffix) for date and PolityName columns, Side from join keys
target_cols = ['Side', 'WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']

df_join = pd.DataFrame()
df_join['Side'] = join_result['Side']
df_join['WarID'] = join_result['WarID']
df_join['PolityID'] = join_result['PolityID']

for col in ['StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']:
    col_union = col + '_union'
    if col_union in join_result.columns:
        df_join[col] = join_result[col_union]
    else:
        # fallback if missing, use join side
        col_join = col + '_join'
        if col_join in join_result.columns:
            df_join[col] = join_result[col_join]
        else:
            df_join[col] = pd.NA

# Concatenate join_result and union_result
final_df = pd.concat([df_join, union_result], ignore_index=True)

# Convert columns to correct types
int_cols = ['WarID', 'PolityID', 'StartYear', 'StartMonth', 'StartDay', 'EndYear', 'EndMonth', 'EndDay', 'IsInitiator', 'Outcome', 'Deaths', 'PolityName']
for c in int_cols:
    final_df[c] = pd.to_numeric(final_df[c], errors='coerce').astype('Int64')

final_df = final_df[target_cols]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_51/target_multisource_mcts.csv", index=False)