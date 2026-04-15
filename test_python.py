import pandas as pd


def main():
    source0_path = "autopipeline-benchmarks/github-pipelines/length1_9/test_0.csv"
    target_path = "autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_critique_history.csv"

    # Read source CSV with index_col=0 to ignore the numerical index column
    df = pd.read_csv(source0_path, index_col=0)

    # Group by 'zipcode' and 'AGI_STUB'
    # Aggregate 'N1' and 'A00100' by sum
    grouped = df.groupby(["zipcode", "AGI_STUB"], as_index=False).agg({
        "N1": "sum",
        "A00100": "sum"
    })

    # Ensure columns are in the correct order as target schema
    grouped = grouped[["zipcode", "AGI_STUB", "N1", "A00100"]]

    # Ensure data types match target schema
    grouped = grouped.astype({
        "zipcode": int,
        "AGI_STUB": int,
        "N1": int,
        "A00100": int
    })

    # Write the transformed data to the target CSV file without the index
    grouped.to_csv(target_path, index=False)


if __name__ == "__main__":
    main()