# Transchema

## Overview

This repository contains Python scripts designed to automate the generation of SQL/Python queries using the GPT-3.5/GPT-4.0 model from OpenAI. It also includes utility functions for database operations, file reading, logging, and similarity calculations.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Contributing](#contributing)

---

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/asu-cactus/transchema.git
    ```
2. Navigate to the project directory:
    ```bash
    cd transchema
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```  
---

## Usage

1. Create a environment variable with your OpenAI API key.
    ```
    export OPENAI_API_KEY={your_openai_api_key}
    ```
2. Pick a dataset from out benchmark: {‘Smart Building’, ‘COVID-19 & Machine Log’,Commercial dataset-1’, ‘Commercial dataset-2’} and change the ‘excel_file_path’ and ‘json_file_path’ in ‘excel2json.py’ accordingly. Here is the link for the benchmark dataset <[link](https://github.com/asu-cactus/Data_Transformation_Benchmark)>
    ````
    # Path to the Excel file
    excel_file_path = '<dataset_you_picked>.xlsx'
    
    
    # Path to save the JSON file
    json_file_path = <dataset_you_picked>.json'
    ```
3. Run the `excel2json.py` script to convert the .xlsx benchmark dataset to .json format:
    ```bash
    python excel2json.py
    ```
4. You can set the configurations in experiment_multistep.sh. Here's an example
    ```
python3 critique_data.py \
  # ─── Experiment scope ──────────────────────────────────────────────────────
  --len-id 5 \                            # start pipeline length directory (e.g. length5)  
  --max-len-id 5 \                        # end pipeline length directory (inclusive)  
  --target-id 12 \                        # start target table ID for experiment  
  --max-target-id 40 \                    # end target table ID for experiment  

  # ─── Sampling configuration ────────────────────────────────────────────────
  --no-perc \                             # disable percentage-based sampling (use fixed --target-length)  
  --target-per 25 \                       # % of target rows to sample (only if using percentage)  
  --target-length 3 \                     # fixed number of target samples (when --no-perc)  
  --source-length 9 \                     # number of source samples to include in prompt  

  # ─── Hint selection & anonymization ────────────────────────────────────────
  --hint-source v3 \                      # choose hint set: v1_kv, v1_text, v2, or v3  
  --no-anon \                             # do NOT anonymize column names in prompts  
  --fd-flag 0 \                           # include (1) or exclude (0) functional‐dependency info  

  # ─── Hint truncation flags & thresholds ───────────────────────────────────
  --join-flag 0 \                         # truncate join hints? 0=no (all), 1=yes (apply thresholds)  
  --join-hints-truncate \
    0.027387593197926163 \
    0.8763891522960383 \
    0.6923226156693141 \
    0.8946066635038473 \
    0.14038693859523377 \
    0.8007445686755367 \                 # 6 thresholds for join-hint truncation  

  --aggregate-flag 0 \                    # truncate aggregate hints? 0=no, 1=yes  
  --aggregate-hints-truncate \
    0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 0.9 0.1 \ # 10 thresholds for aggregate-hint truncation  

  --hints-v3-truncates \
    '{"t1":0.7,"t2":0.7,"t3":0.7,"t4":10,"t5":0.1,"t6":0.8,"t7":0.4,"t8":0.3,"t9":0.2,"t10":0.3,"t11":0.5,"t12":0.7,"t13":0.2}' \
    # JSON mapping for v3 text-hint truncation parameters  

  # ─── Prompt & model configuration ──────────────────────────────────────────
  --token-limit 120000 \                  # max tokens per prompt (affects context size)  
  --model gpt-4-turbo \                   # model to use: gpt-4-turbo or gpt-4.1-mini  

  # ─── Logging & experiment metadata ────────────────────────────────────────
  --log-dir logs-auto-suggest-llm-21-04 \ # where to write logs  
  --experiment-name feature_v3_2 \        # experiment identifier (used in filenames)  
  --no-of-runs 1                          # how many times to repeat each configuration  

    ```
4.  Run the run.py script to start the experiment:
    ```bash
    experiment_multistep.sh
    ```

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

## Contributing

Feel free to fork the project and submit a pull request with your changes!

---


