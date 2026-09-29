import os
import shutil

def reorganize_files(source_dir, target_dir_base):
    # Ensure the base target directory exists
    if not os.path.exists(target_dir_base):
        os.makedirs(target_dir_base)

    # List all files in the source directory
    files = os.listdir(source_dir)
    target_file = "Target4.csv"  # This is considered as the main target file
    prefix = target_file.split('.')[0]  # Get prefix before the file extension

    # Collect test files with the same prefix
    test_files = [file for file in files if file.startswith(prefix + "_")]

    # Organize files into new directories
    target_index = 4
    for i, test_file in enumerate(test_files):
        new_target_dir = os.path.join(target_dir_base, f"target{target_index}_{i}")
        os.makedirs(new_target_dir, exist_ok=True)

        # Copy the main target file into each new directory
        shutil.copy(os.path.join(source_dir, target_file), os.path.join(new_target_dir, "target.csv"))

        # Move each test file into its respective directory and rename it
        shutil.move(os.path.join(source_dir, test_file), os.path.join(new_target_dir, "test_0.csv"))

    print(f"All files have been reorganized under {target_dir_base}.")
# Specify the source directory and the base directory for the new structure
source_directory = 'D:/transchema\smart_building/14NGRID'
target_directory_base = 'D:/transchema\smart_building'

reorganize_files(source_directory, target_directory_base)