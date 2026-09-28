import pandas as pd
import re

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_85/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length2_85/training_1.csv', index_col=0)

def extract_int_mouse_id(s):
    m = re.search(r'\d+', s)
    return int(m.group()) if m else None

df0['Mouse ID'] = df0['Mouse ID'].map(extract_int_mouse_id)
df1['Mouse ID'] = df1['Mouse ID'].map(extract_int_mouse_id)

df = pd.merge(df0, df1, on='Mouse ID', how='inner')

result = df[['Drug', 'Timepoint', 'Mouse ID']]

result.to_csv('autopipeline-benchmarks/github-pipelines/length2_85/target_multisource_mcts.csv', index=False)