import pandas as pd

def main():
    # File paths for the source tables
    source0_path = 'autopipeline-benchmarks/github-pipelines/length4_73/test_0.csv'
    source1_path = 'autopipeline-benchmarks/github-pipelines/length4_73/test_1.csv'

    # Load source tables (ignore the first auto‐generated index column)
    df0 = pd.read_csv(source0_path, index_col=0)
    df1 = pd.read_csv(source1_path, index_col=0)

    # ----------------------------------------------------------------------------
    # Operation 1: GROUP BY and AGGREGATIONS
    #   group_by: Source4_73_0.city, Source4_73_1.type (we also need Source4_73_1.city
    #             so we can later join on it)
    #   aggregations:
    #     - AVG(Source4_73_0.fare)
    #     - COUNT(Source4_73_0.ride_id)
    #     - SUM(Source4_73_1.driver_count)
    # ----------------------------------------------------------------------------

    # Aggregate Source4_73_0 by city
    agg0 = (
        df0
        .groupby('city', as_index=False)
        .agg(
            **{
                'Average Fare ($)': ('fare', 'mean'),
                'Number of Rides': ('ride_id', 'count'),
            }
        )
    )

    # Aggregate Source4_73_1 by city and type
    agg1 = (
        df1
        .groupby(['city', 'type'], as_index=False)
        .agg(
            **{
                'Number of Drivers': ('driver_count', 'sum'),
            }
        )
    )
    # Rename columns to match target schema
    agg1 = agg1.rename(columns={'type': 'City Type'})

    # Rename city column in both aggregates to a common name "City" for the join
    agg0 = agg0.rename(columns={'city': 'City'})
    agg1 = agg1.rename(columns={'city': 'City'})

    # ----------------------------------------------------------------------------
    # Operation 2: JOIN
    #   join agg0 and agg1 on City
    # ----------------------------------------------------------------------------
    result = pd.merge(
        left=agg0,
        right=agg1,
        on='City',
        how='inner'
    )

    # Reorder columns to exactly match target schema
    result = result[
        ['City', 'Average Fare ($)', 'Number of Rides', 'Number of Drivers', 'City Type']
    ]

    # Write final result to CSV
    output_path = 'autopipeline-benchmarks/github-pipelines/length4_73/target_multisource.csv'
    result.to_csv(output_path, index=False)
    print(f"Transformation complete. Output written to: {output_path}")

if __name__ == '__main__':
    main()