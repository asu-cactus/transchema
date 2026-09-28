import pandas as pd

source0_path = "autopipeline-benchmarks/github-pipelines/length3_43/training_0.csv"
source1_path = "autopipeline-benchmarks/github-pipelines/length3_43/training_1.csv"
target_path = "autopipeline-benchmarks/github-pipelines/length3_43/target_multisource_mcts.csv"

df0 = pd.read_csv(source0_path, index_col=0)
df1 = pd.read_csv(source1_path, index_col=0)

agg_scores = df1.groupby('school_name').agg({'math_score':'mean', 'reading_score':'mean'}).reset_index()

merged = pd.merge(agg_scores, df0, on='school_name', how='inner')

agg_final = merged.groupby('type').agg({
    'size':'sum',
    'budget':'sum',
    'math_score':'mean',
    'reading_score':'mean'
}).reset_index()

agg_final = agg_final.rename(columns={
    'size':'Total Students',
    'budget':'Total School Budget',
    'math_score':'Average Math Score',
    'reading_score':'Average Reading Score'
})

agg_final['School Size'] = agg_final['Total Students'].astype(float)
agg_final['Total Students'] = agg_final['Total Students'].astype(float)
agg_final['Total School Budget'] = agg_final['Total School Budget'].astype(float)
agg_final['Average Math Score'] = agg_final['Average Math Score'].astype(float)
agg_final['Average Reading Score'] = agg_final['Average Reading Score'].astype(float)
agg_final['type'] = agg_final['type'].astype(str)

agg_final.to_csv(target_path, index=False)