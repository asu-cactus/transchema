import pandas as pd

# Load the source CSV
source_path_0 = 'autopipeline-benchmarks/github-pipelines/length4_85/test_0.csv'
df_source_0 = pd.read_csv(source_path_0, index_col=0)

# Group by 'crit_cn' and count number of critics per 'crit_cn'
# Since target example has 'critic' as integer, assume count of rows per crit_cn
df_target = df_source_0.groupby('crit_cn', as_index=False).agg({'critic': 'count'})

# Rename columns to match target schema exactly
df_target.rename(columns={'critic': 'critic'}, inplace=True)

# Ensure 'crit_cn' is string and 'critic' is integer
df_target['crit_cn'] = df_target['crit_cn'].astype(str)
df_target['critic'] = df_target['critic'].astype(int)

# Save to target path
target_path = 'autopipeline-benchmarks/github-pipelines/length4_85/target_multisource_cot.csv'
df_target.to_csv(target_path, index=False)