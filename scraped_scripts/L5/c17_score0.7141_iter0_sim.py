import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length5_17/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length5_17/training_5.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

df['S/N'] = df['S/N'].astype(int)
df['Postal District'] = df['Postal District'].astype(int)
df['Monthly Gross Rent($)'] = df['Monthly Gross Rent($)'].astype(int)

df = df.rename(columns={'Floor Area (sq ft)': 'Floor Area (sq ft)'})  # no rename needed, just to keep consistent

df = df[['S/N', 'Building/Project Name', 'Street Name', 'Postal District', 'Type',
         'No. of Bedroom(for Non-Landed Only)', 'Monthly Gross Rent($)', 'Floor Area (sq ft)', 'Lease Commencement Date']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length5_17/target_multisource_mcts.csv", index=False)