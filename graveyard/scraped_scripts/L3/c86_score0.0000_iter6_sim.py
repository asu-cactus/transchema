import pandas as pd

src0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_0.csv", index_col=0)
src1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_1.csv", index_col=0)
src2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_86/training_2.csv", index_col=0)

union_result = pd.concat([src0, src0], ignore_index=True)

join_result_1 = pd.merge(union_result, src1, left_on="Country Name", right_on="Country", how="inner")

join_result_2 = pd.merge(join_result_1, src2, left_on="Country Name", right_on="Country", how="inner")

df = join_result_2.rename(columns={
    "Rank": "Rank",
    "Documents": "Documents",
    "Citable documents": "Citable documents",
    "Citations": "Citations",
    "Self-citations": "Self-citations",
    "Citations per document": "Citations per document",
    "H index": "H index",
    "Energy Supply": "Energy Supply",
    "Energy Supply per Capita": "Energy Supply per Capita",
    "% Renewable": "% Renewable"
})

# Select and convert columns to int as per target schema
cols_int = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
            'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']

for c in cols_int:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

years = [str(y) for y in range(2006, 2016+1)]
for y in years:
    df[y] = pd.to_numeric(df[y], errors='coerce').fillna(0).astype(int)

target_cols = ['Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations',
               'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita',
               '% Renewable'] + years

df_target = df[target_cols]

df_target.to_csv("autopipeline-benchmarks/github-pipelines/length3_86/target_multisource_mcts.csv", index=False)