import pandas as pd

source1_path = "autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv"
source2_path = "autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv"

df1 = pd.read_csv(source1_path, index_col=0)
df2 = pd.read_csv(source2_path, index_col=0)

union_df = pd.concat([df1, df1], ignore_index=True)

merged = pd.merge(union_df, df2, how='left', on='Country')

cols = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
        'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita',
        '% Renewable']

result = merged[cols]

int_cols = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
            'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita',
            '% Renewable']

for c in int_cols:
    result[c] = pd.to_numeric(result[c], errors='coerce').round().astype('Int64')

for year in range(2006, 2016):
    result[str(year)] = 1

result.to_csv(target_path, index=False)