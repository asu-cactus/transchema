import pandas as pd

source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

union_result = pd.concat([source1, source1], ignore_index=True)

merged = pd.merge(union_result, source2, on="Country", how="left")

cols_int = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'H index',
            'Energy Supply', 'Energy Supply per Capita', '% Renewable']
for c in cols_int:
    if c in merged.columns:
        merged[c] = pd.to_numeric(merged[c], errors='coerce').fillna(0).astype(int)

merged['Citations per document'] = pd.to_numeric(merged['Citations per document'], errors='coerce').fillna(0).round().astype(int)

target_cols = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
               'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita',
               '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']

for year in ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015']:
    if year not in merged.columns:
        merged[year] = 0
    else:
        merged[year] = pd.to_numeric(merged[year], errors='coerce').fillna(0).astype(int)

result = merged[target_cols]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)