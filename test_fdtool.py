import pandas as pd
import pdb
import numpy as np
from quality.quality import (
    analyze_functional_dependencies_deprecated1,
    analyze_functional_dependencies,
)


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
    filtered_fds, all_keys_sorted = analyze_functional_dependencies_deprecated1(df)
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
    df = generate_test_data()

    test_analyze_functional_dependencies(df)
