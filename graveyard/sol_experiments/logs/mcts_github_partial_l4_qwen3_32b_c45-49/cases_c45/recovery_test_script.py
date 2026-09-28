import pandas as pd

# Load all source tables
src0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_45/test_0.csv', index_col=0)
src1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_45/test_1.csv', index_col=0)
src2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_45/test_2.csv', index_col=0)
src3 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_45/test_3.csv', index_col=0)

# Standardize columns across all sources
for df in [src0, src1, src2, src3]:
    df['WarShortName'] = df['WarID'].astype(int)
    if 'IsIntervention' not in df.columns:
        df['IsIntervention'] = 0
    if 'IsInternational' not in df.columns:
        df['IsInternational'] = 0

# Combine all sources
result = pd.concat([src0, src1, src2, src3], ignore_index=True)

# Filter to match target schema
result = result[['WarType', 'WarID', 'WarShortName', 'IsInternational', 'IsIntervention']]

# Save final output
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_45/target_multisource_mcts_recovery_test_val.csv', index=False)