import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_75/training_1.csv", index_col=0)

# Map school_name in source1 to type using source0
school_type_map = source0.set_index('school_name')['type']
source1['type'] = source1['school_name'].map(school_type_map)

# Aggregate reading_score and math_score by type
agg = source1.groupby('type', as_index=False).agg({'reading_score':'mean', 'math_score':'mean'})

# Rename columns to match target schema
agg = agg.rename(columns={'type':'type', 'reading_score':'a', 'math_score':'b'})

agg.to_csv("autopipeline-benchmarks/github-pipelines/length4_75/target_multisource_mcts.csv", index=False)