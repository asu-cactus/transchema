import pandas as pd

def normalize_incident_type(s):
    s = s.str.upper().str.strip()
    s = s.str.replace(r'[^A-Z0-9]', '', regex=True)
    mapping = {
        'GRAFFITI': 1,
        'ASSAULTS': 2,
        'SUICIDEATTEMPTSTHREATS': 3,
        'BULLYING': 4,
        'DRUGSALCOHOLOFFENSE': 5,
        'FIREINCENDIARY': 6,
        'HARASSMENT': 7,
        'THREATS': 8,
        'ASSAULT': 2,
        'ASSAULTS': 2,
        'DISORDERLYCONDUCT': 9,
        'DRUGANDALCOHOLOFFENSES': 5,
        # Add more mappings if needed dynamically below
    }
    # Map known keys, else assign unique integer codes dynamically
    codes = {}
    next_code = max(mapping.values()) + 1
    result = []
    for val in s:
        if val in mapping:
            result.append(mapping[val])
        else:
            if val not in codes:
                codes[val] = next_code
                next_code += 1
            result.append(codes[val])
    return pd.Series(result, index=s.index)

def main():
    paths = [
        "autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv"
    ]
    dfs = []
    for i, path in enumerate(paths):
        df = pd.read_csv(path, index_col=0)
        df['INCIDENT_TYPE'] = normalize_incident_type(df['INCIDENT_TYPE'])
        agg = df.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
        dfs.append(agg)
    result = pd.concat(dfs, ignore_index=True)
    result = result.groupby(['SCHOOL_YEAR', 'ULCS_NO', 'INCIDENT_TYPE', 'SCHOOL_ID'], as_index=False)['INCIDENT_COUNT'].sum()
    result = result.astype({
        'SCHOOL_YEAR': str,
        'ULCS_NO': int,
        'INCIDENT_TYPE': int,
        'INCIDENT_COUNT': int,
        'SCHOOL_ID': int
    })
    result.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)

if __name__ == "__main__":
    main()