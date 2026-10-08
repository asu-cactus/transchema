import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length5_30/training_1.csv"
output_path = "autopipeline-benchmarks/github-pipelines/length5_30/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

pivot = df1.set_index(['Student ID', 'school_name'])[['math_score', 'reading_score']]

pivot = pivot.reset_index()

merged = pd.merge(pivot, df0[['school_name', 'budget']], on='school_name', how='left')

merged = merged[['school_name', 'Student ID', 'budget', 'math_score', 'reading_score']]

merged['Student ID'] = merged['Student ID'].astype(int)
merged['budget'] = merged['budget'].astype(int)
merged['math_score'] = merged['math_score'].astype(float)
merged['reading_score'] = merged['reading_score'].astype(float)
merged['school_name'] = merged['school_name'].astype(str)

merged.to_csv(output_path, index=False)