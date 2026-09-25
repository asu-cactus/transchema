import pandas as pd

def main():
    paths = [
        "autopipeline-benchmarks/github-pipelines/length4_56/training_0.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_1.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_2.csv",
        "autopipeline-benchmarks/github-pipelines/length4_56/training_3.csv"
    ]

    # Read each source and aggregate counts by SCHOOL_YEAR
    df0 = pd.read_csv(paths[0], index_col=0)
    agg0 = df0.groupby('SCHOOL_YEAR', as_index=False).size()
    agg0.columns = ['SCHOOL_YEAR', 'ULCS_NO']

    df1 = pd.read_csv(paths[1], index_col=0)
    agg1 = df1.groupby('SCHOOL_YEAR', as_index=False).size()
    agg1.columns = ['SCHOOL_YEAR', 'INCIDENT_TYPE']

    df2 = pd.read_csv(paths[2], index_col=0)
    agg2 = df2.groupby('SCHOOL_YEAR', as_index=False).size()
    agg2.columns = ['SCHOOL_YEAR', 'INCIDENT_COUNT']

    df3 = pd.read_csv(paths[3], index_col=0)
    agg3 = df3.groupby('SCHOOL_YEAR', as_index=False).size()
    agg3.columns = ['SCHOOL_YEAR', 'SCHOOL_ID']

    # Join all aggregated counts on SCHOOL_YEAR
    # Use inner join to keep only SCHOOL_YEAR present in all sources (matches target examples)
    merged = agg0.merge(agg1, on='SCHOOL_YEAR', how='inner') \
                 .merge(agg2, on='SCHOOL_YEAR', how='inner') \
                 .merge(agg3, on='SCHOOL_YEAR', how='inner')

    # Cast columns to correct types as per target schema
    merged = merged.astype({
        'SCHOOL_YEAR': str,
        'ULCS_NO': int,
        'INCIDENT_TYPE': int,
        'INCIDENT_COUNT': int,
        'SCHOOL_ID': int
    })

    merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_56/target_multisource_mcts.csv", index=False)

if __name__ == "__main__":
    main()