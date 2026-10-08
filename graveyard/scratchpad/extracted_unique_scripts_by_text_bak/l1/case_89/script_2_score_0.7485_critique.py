import pandas as pd
import glob
import os
from functools import reduce

src_dir = "autopipeline-benchmarks/github-pipelines/length1_89/"
src_pattern = os.path.join(src_dir, "training_*.csv")
src_files = sorted(glob.glob(src_pattern))

dfs = []
for f in src_files:
    df = pd.read_csv(f, index_col=0)
    df['date'] = df['date'].astype(str)
    df['ticker'] = df['ticker'].astype(float)
    pivot = df.pivot(index='date', columns='ticker', values='close')
    pivot.columns = pivot.columns.astype(str)
    dfs.append(pivot)

df_joined = reduce(lambda left, right: pd.merge(left, right, how='outer', left_index=True, right_index=True), dfs)

df_joined.reset_index(inplace=True)

cols = df_joined.columns.tolist()
new_cols = []
for c in cols:
    if c == 'date':
        new_cols.append(c)
    else:
        try:
            new_cols.append(float(c))
        except:
            new_cols.append(c)
df_joined.columns = new_cols

sorted_cols = ['date'] + sorted([c for c in df_joined.columns if c != 'date'])
df_joined = df_joined[sorted_cols]

df_joined.to_csv(os.path.join(src_dir, "target_multisource_mcts.csv"), index=False)