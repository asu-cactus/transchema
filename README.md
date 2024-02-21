# ChatGPTwithSQLscript

## Overview

This repository contains Python scripts designed to automate the generation of SQL queries using the GPT-3.5 model from OpenAI. It also includes utility functions for database operations, file reading, logging, and similarity calculations.

---

## Table of Contents

- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Contributing](#contributing)

---

## Dependencies

- Python 3.8+
- `pandas`
- `openai`
- `matplotlib`
- `seaborn`
- `sqlparse`
- `psycopg2-binary`
- `numpy`
- `sklearn`

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/asu-cactus/ChatGPTwithSQLscript.git
    ```
2. Navigate to the project directory:
    ```bash
    cd ChatGPTwithSQLscript
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

1. Create a `config.py` file and put your OpenAI API key there.
    ```
    OPENAI_API_KEY = "{your_openai_api_key}"
    ```
2. Run the run.py script to start the experiment:
    ```bash
    python run.py
    ```
3. Pick a dataset from out benchmark: {‘Smart Building’, ‘COVID-19 & Machine Log’,Commercial dataset-1’, ‘Commercial dataset-2’} and change the ‘excel_file_path’ and ‘json_file_path’ in ‘excel2json.py’ accordingly. Here is the link for the benchmark dataset <[link](https://github.com/asu-cactus/Data_Transformation_Benchmark)>
    ````
    # Path to the Excel file
    excel_file_path = '<dataset_you_picked>.xlsx'
    
    
    # Path to save the JSON file
    json_file_path = <dataset_you_picked>.json'
    ```
4. Run the `excel2json.py` script to convert the .xlsx benchmark dataset to .json format:
    ```bash
    python excel2json.py
    ```
5. You can set the configurations such as template_option, source, target in run.py. Here's an example
    ```
    template_option = 1
    target_id, max_target_id = 10, 10
    source_id, max_source_id = 1, 1
    ```
    `target_id`,`max_target_id` mean the first group and the last group the script will iterate. `source_id`, `max_source_id` mean the first source and the last source the script will iterate.
6.  Run the run.py script to start the experiment:
    ```bash
    python run.py
    ```
Note: Detailed template_option are in the gpt.py. Option 3 and 4 both belong to Option 3 in the paper, and Option 5 corresponds to Option 4 in the paper, etc.

---

For the github benchmark, please download the content of the following link and put the 'github-pipelines' folder here: https://gitlab.com/jwjwyoung/autopipeline-benchmarks

Then, do the following steps:

1. run the react/pre_processing/remove_id_columns.py script to remove the id columns from the datasets
2. run the react/pre_processing/clean.py script to clean the dataset for length1_16, length1_40, and length1_59.
3. rename the react/github-pipelines/length1_16/test_0.csv to react/github-pipelines/length1_16/test_0_dirty.csv for backup
4. rename the react/github-pipelines/length1_40/test_0_removed.csv to react/github-pipelines/length1_40/test_0.csv
5. replace the test_0.csv in react/github-pipelines/length1_59 and react/github-pipelines/length1_40 with the test_0.csv in react/github-pipelines/length1_16
6. to get output.xlsx, run the react/pre_processing/generate_output.py

7. to get the json file, run the react/pre_processing/excel2json.py

---

## Scripts

- `excel2json.py`: Converts Excel data to JSON format.
- `gpt.py`: Interacts with the GPT-3 model to generate SQL queries.
- `join.py`: Handles JOIN operations in SQL.
- `run.py`: Main script to run the experiments.
- `sql_complexity_analyzer.py`: Analyzes the complexity of SQL queries.
- `util.py`: Contains utility functions for database operations and more.

---

## Contributing

Feel free to fork the project and submit a pull request with your changes!

---


