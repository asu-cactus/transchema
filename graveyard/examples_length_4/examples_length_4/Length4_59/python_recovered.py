import pandas as pd

# Define source file paths
source_files = [
    "autopipeline-benchmarks/github-pipelines/length4_59/test_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/test_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/test_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_59/test_3.csv",
]

def clean_numeric_column(s):
    # Remove non-breaking spaces and regular spaces, then convert to int
    # Some numbers have spaces as thousand separators, e.g., "7 715 778"
    if pd.isna(s):
        return 0
    return int(s.replace("\xa0", "").replace(" ", "").replace(",", ""))

def load_and_clean_source(path):
    df = pd.read_csv(path, index_col=0)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Clean numeric columns: 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total'
    # 'N.°' and 'Municipio' should be integers, but some may be read as int or str; enforce int
    for col in ['N.°', 'Municipio']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    for col in ['Población cabecera', 'Población resto', 'Población Total']:
        df[col] = df[col].astype(str).map(clean_numeric_column)

    # Standardize Departamento strings: strip whitespace
    df['Departamento'] = df['Departamento'].str.strip()

    return df

def main():
    # Load and clean all source dataframes
    dfs = [load_and_clean_source(f) for f in source_files]

    # All source tables have the EXACT same schema
    # So Union all of them (concat) vertically to get combined data
    combined_df = pd.concat(dfs, ignore_index=True)

    # According to target examples, column order and types must be:
    # ['Departamento': string, 'N.°': integer, 'Municipio': integer,
    #  'Población cabecera': integer, 'Población resto': integer, 'Población Total': integer]

    # Reorder columns to match target schema just in case (source columns are in same order but confirm)
    combined_df = combined_df[['Departamento', 'N.°', 'Municipio', 'Población cabecera', 'Población resto', 'Población Total']]

    # Final type enforcement
    combined_df['Departamento'] = combined_df['Departamento'].astype(str)
    combined_df['N.°'] = combined_df['N.°'].astype(int)
    combined_df['Municipio'] = combined_df['Municipio'].astype(int)
    combined_df['Población cabecera'] = combined_df['Población cabecera'].astype(int)
    combined_df['Población resto'] = combined_df['Población resto'].astype(int)
    combined_df['Población Total'] = combined_df['Población Total'].astype(int)

    # There is no indication of duplicate elimination or group by in the prompt or examples,
    # so output is just the union of all source rows.

    # Write the result to the target CSV path with index=False
    combined_df.to_csv("autopipeline-benchmarks/github-pipelines/length4_59/target_multisource_cot.csv", index=False)

if __name__ == "__main__":
    main()