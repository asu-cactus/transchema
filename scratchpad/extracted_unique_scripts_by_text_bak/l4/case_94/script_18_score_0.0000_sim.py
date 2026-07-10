import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv", index_col=0)

df_01 = pd.merge(df0, df1, on=['SubjectId', 'Split'], suffixes=('_0', '_1'))
df_012 = pd.merge(df_01, df2, on=['SubjectId', 'Split'])
df_all = pd.merge(df_012, df3, on=['SubjectId', 'Split'], suffixes=('', '_3'))

# We have columns from all sources, but the target schema expects one row per (Split, SubjectId)
# with columns: Split, SubjectId, Subject, PA, AB, H, TB, BB, SF, HBP
# The 'Subject' column in target is integer, but source 'Subject' columns are strings like 'HitterId', 'PitcherTeamId', etc.
# The target examples show Subject column as integer equal to SubjectId, so we will set Subject = SubjectId.

# The source columns for stats are duplicated from multiple sources, so we sum them up per (Split, SubjectId)
# The columns to sum are PA, AB, H, TB, BB, SF, HBP from all sources.

# Extract and sum numeric columns from all sources
cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

# For df0 and df1, columns are suffixed _0 and _1 after first merge, for df2 no suffix, for df3 suffixed _3
# After merges, columns are:
# From df0: PA_0, AB_0, H_0, TB_0, BB_0, SF_0, HBP_0
# From df1: PA_1, AB_1, H_1, TB_1, BB_1, SF_1, HBP_1
# From df2: PA, AB, H, TB, BB, SF, HBP
# From df3: PA_3, AB_3, H_3, TB_3, BB_3, SF_3, HBP_3

# Sum all these columns row-wise, treating missing columns as 0

def safe_col_sum(df, col_bases):
    total = 0
    for base in col_bases:
        for suffix in ['_0', '_1', '', '_3']:
            col = base + suffix
            if col in df.columns:
                total = total + df[col].fillna(0).astype(int)
    return total

result = pd.DataFrame()
result['Split'] = df_all['Split']
result['SubjectId'] = df_all['SubjectId']
result['Subject'] = df_all['SubjectId'].astype(int)

for col in cols:
    result[col] = 0
    for suffix in ['_0', '_1', '', '_3']:
        colname = col + suffix
        if colname in df_all.columns:
            result[col] += df_all[colname].fillna(0).astype(int)

result = result.astype({'Split': str, 'SubjectId': int, 'Subject': int,
                        'PA': int, 'AB': int, 'H': int, 'TB': int, 'BB': int, 'SF': int, 'HBP': int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)