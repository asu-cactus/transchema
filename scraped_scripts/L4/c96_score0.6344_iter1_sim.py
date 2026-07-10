import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_96/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_96/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['Split'] = df['Split'].str.extract(r'(\d+)').astype(int, errors='ignore').fillna(df['Split'])
df['Subject'] = pd.to_numeric(df['Subject'], errors='coerce').fillna(df['Subject'])

if df['Split'].dtype == object:
    # If still object, try mapping known strings to integers if possible
    # But no hardcoding, so leave as is
    pass
else:
    df['Split'] = df['Split'].astype(int)

if df['Subject'].dtype == object:
    # Try to convert to int if possible
    try:
        df['Subject'] = df['Subject'].astype(int)
    except:
        pass
else:
    df['Subject'] = df['Subject'].astype(int)

# The target schema columns are:
# ['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
# The source tables already have these columns, but Split and Subject are strings in source.
# We convert Split and Subject to integers if possible.

# If 'Split' and 'Subject' are categorical strings like 'vs RHP', 'HitterId', etc., 
# we convert them to integer codes.

if df['Split'].dtype == object:
    df['Split'] = df['Split'].astype('category').cat.codes

if df['Subject'].dtype == object:
    df['Subject'] = df['Subject'].astype('category').cat.codes

# Ensure all numeric columns are int
for col in ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

df = df[['SubjectId', 'Split', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']]

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_96/target_multisource_mcts.csv", index=False)