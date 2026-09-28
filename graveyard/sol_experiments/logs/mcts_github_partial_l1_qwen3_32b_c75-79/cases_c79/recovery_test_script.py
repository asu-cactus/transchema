import pandas as pd

# Read source files
source0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_79/test_0.csv', index_col=0)
source1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_79/test_1.csv', index_col=0)

# Process 2015 source - rename columns
source1_15 = source1.rename(columns={
    'Happiness Rank': 'Happiness_Rank_15',
    'Happiness Score': 'Happiness_Score_15',
    'Standard Error': 'Standard_Error_15',
    'Economy (GDP per Capita)': 'Economy_15',
    'Health (Life Expectancy)': 'Life_Expectancy_15',
    'Trust (Government Corruption)': 'Trust_15',
    'Dystopia Residual': 'Dystopia_15'
})

# Add missing suffixes to columns
col_map = {
    'Family': 'Family_15',
    'Freedom': 'Freedom_15',
    'Generosity': 'Generosity_15'
}
source1_15 = source1_15.rename(columns=col_map)

# Select final columns for 2015 data
source1_15 = source1_15[
    ['Country', 'Region', 'Happiness_Rank_15', 'Happiness_Score_15', 'Standard_Error_15', 
     'Economy_15', 'Family_15', 'Life_Expectancy_15', 'Freedom_15', 'Trust_15', 'Generosity_15', 'Dystopia_15']
]

# Join with 2017 data
result = pd.merge(source1_15, source0, on='Country', how='inner')

# Save result to target file
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_79/target_multisource_mcts_recovery_test_val.csv', index=False)