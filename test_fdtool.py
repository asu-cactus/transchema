import pandas as pd
import pdb
import numpy as np
from quality.quality import (
    analyze_functional_dependencies_deprecated,
    analyze_functional_dependencies,
)

import pandas as pd
import itertools


def generate_data_1() -> pd.DataFrame:
    """
    Generate a DataFrame with two composite keys and a payload column:
      - Composite Key 1: key1_part1, key1_part2 (10×10 grid → 100 unique pairs)
      - Composite Key 2: key2_part1, key2_part2 (4×25 grid → 100 unique pairs)
      - value: an integer payload from 0 to 99
    """
    # 1) Define the domains for each part of the two composite keys
    key1_vals1 = [f"K1_A{i}" for i in range(10)]
    key1_vals2 = [f"K1_B{j}" for j in range(10)]
    pairs1 = list(itertools.product(key1_vals1, key1_vals2))

    key2_vals1 = [f"K2_C{i}" for i in range(4)]
    key2_vals2 = [f"K2_D{j}" for j in range(25)]
    pairs2 = list(itertools.product(key2_vals1, key2_vals2))

    # 2) Truncate both lists to the same length
    n = min(len(pairs1), len(pairs2))
    pairs1 = pairs1[:n]
    pairs2 = pairs2[:n]

    # 3) Build the DataFrame
    df = pd.DataFrame(
        {
            "key1_part1": [p[0] for p in pairs1],
            "key1_part2": [p[1] for p in pairs1],
            "key2_part1": [q[0] for q in pairs2],
            "key2_part2": [q[1] for q in pairs2],
            "value": list(range(n)),
        }
    )

    # 4) (Optional) Verify uniqueness of each composite key
    assert not df.duplicated(
        subset=["key1_part1", "key1_part2"]
    ).any(), "Composite Key 1 is not unique!"
    assert not df.duplicated(
        subset=["key2_part1", "key2_part2"]
    ).any(), "Composite Key 2 is not unique!"

    return df


def generate_test_data(n_samples=1000):
    key_columns = ["StudentID", "CourseID", "InstructorID"]

    # Generate random data using numpy for faster execution

    # Use numpy random generators for vectorized operations
    student_ids = np.random.randint(1, 11, size=n_samples)  # 1-10 inclusive
    course_ids = np.random.randint(1, 11, size=n_samples)  # 1-5 inclusive
    instructor_ids = np.random.randint(1, 5, size=n_samples)  # 1-3 inclusive
    grade_values = np.random.randint(0, 10, size=n_samples)  # 0-9 inclusive

    # Create DataFrame directly from numpy arrays
    df = pd.DataFrame(
        {
            "StudentID": student_ids,
            "CourseID": course_ids,
            "InstructorID": instructor_ids,
            "Grade": grade_values,
        }
    )

    # Ensure that the key columns are unique
    df = df.drop_duplicates(subset=key_columns).reset_index(drop=True)
    return df


def test_analyze_functional_dependencies(df):
    # Analyze functional dependencies
    filtered_fds, all_keys_sorted = analyze_functional_dependencies_deprecated(df)
    print("Functional Dependencies Analysis Result:")
    print(f"Filtered Functional Dependencies: {filtered_fds}")
    print(f"All Keys Sorted: {all_keys_sorted}")

    print("\n\n")
    filtered_fds, all_keys_sorted = analyze_functional_dependencies(df)
    print("Functional Dependencies Analysis Result:")
    print(f"Filtered Functional Dependencies: {filtered_fds}")
    print(f"All Keys Sorted: {all_keys_sorted}")


if __name__ == "__main__":
    # Generate test data
    df = generate_data_1()
    print("Generated DataFrame:")
    print(df)

    test_analyze_functional_dependencies(df)
