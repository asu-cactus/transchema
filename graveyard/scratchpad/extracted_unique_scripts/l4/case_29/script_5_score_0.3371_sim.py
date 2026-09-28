import pandas as pd
import hashlib

def incident_type_to_int(s):
    return int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16) % (10**8)

def school_year_to_int(s):
    # Extract first 4 digits as year, then subtract 1954 to match target examples
    # e.g. "2014-2015" -> 2014 - 1954 = 60
    try:
        year_start = int(s[:4])
        return year_start - 1954
    except:
        return pd.NA

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_29/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_29/training_3.csv"
]

dfs = []
for i, path in enumerate(paths):
    df = pd.read_csv(path, index_col=0)
    # Normalize column order and names if needed
    # Source4_29_2 has SCHOOL_ID before SCHOOL_YEAR, reorder columns to standard
    cols = ['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'INCIDENT_COUNT', 'SCHOOL_ID']
    df = df[cols]
    # Group by keys and sum INCIDENT_COUNT
    grouped = df.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()
    dfs.append(grouped)

union_df = pd.concat(dfs, ignore_index=True)

final_grouped = union_df.groupby(['ULCS_NO', 'SCHOOL_YEAR', 'INCIDENT_TYPE', 'SCHOOL_ID'], dropna=False, as_index=False)['INCIDENT_COUNT'].sum()

final_grouped['SCHOOL_YEAR'] = final_grouped['SCHOOL_YEAR'].astype(str).map(school_year_to_int)
final_grouped['INCIDENT_TYPE'] = final_grouped['INCIDENT_TYPE'].astype(str).map(incident_type_to_int)

final_grouped = final_grouped.astype({
    'ULCS_NO': 'Int64',
    'SCHOOL_YEAR': 'Int64',
    'INCIDENT_TYPE': 'Int64',
    'INCIDENT_COUNT': 'Int64',
    'SCHOOL_ID': 'Int64'
})

final_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length4_29/target_multisource_mcts.csv", index=False)