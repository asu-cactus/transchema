import pandas as pd

# Load source data
source = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_55/test_0.csv', index_col=0)

# Process J_CALL to extract V_GENE
source['V_GENE'] = source['J_CALL'].str.split('*').str[0]

# Output the result with V_GENE column only
result = source[['V_GENE']]

# Save to target CSV
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_55/target_multisource_mcts_recovery_test_val.csv', index=False)