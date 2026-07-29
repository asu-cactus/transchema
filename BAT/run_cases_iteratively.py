#!/usr/bin/env python3
"""
Run MCTS cases one-by-one with evaluation and cleanup.
Continues even if individual cases fail.
"""
import os
import subprocess
import csv
import logging
import shutil
from datetime import datetime

# Configuration
# Default configuration
BASE_PATH = "/home/asurite.ad.asu.edu/jrtandel/transchema/autopipeline-benchmarks/monteprep-pipelines"
RESULT_DIR = "result/monteprep-pipelines/gpt-4.1-mini/execution"
PREDICT_DIR = "predict/monteprep-pipelines/gpt-4.1-mini/execution"
DATA_TYPE = "auto_pipeline"
LENGTH_TYPE = 1
START_NUM = 0
END_NUM = 100
LOG_DIR = "logs"
CLEANUP_RESULTS = True  # Clean up intermediate result JSON files after evaluation
VALIDATION = "hard_match"  # "hard_match" (evaluator's own similarity) or "autopipeline" (validation.hard_match.compare_tables_matching, matches mcts_search.py --validation autopipeline)
MODEL_NAME = "gpt-4.1-mini"  # must be a key in BAT/src/llm/config.py's MODELS dict (e.g. "o4-mini")
CASES = None  # explicit list of case numbers; overrides START_NUM/END_NUM when set

def setup_logging():
    """Setup logging configuration"""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"iterate_cases_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    return logger, log_file

def run_command(cmd, description, logger):
    """Run a shell command and return success status"""
    logger.info(f"Running: {description}")
    logger.debug(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd="/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout per case
        )

        if result.returncode != 0:
            logger.error(f"Command failed with return code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            return False

        logger.info(f"✓ {description} completed successfully")
        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out (1 hour limit): {description}")
        return False
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def cleanup_case_results(case_id, logger):
    """Delete intermediate JSON result files for a case"""
    if not CLEANUP_RESULTS:
        return

    result_json = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        RESULT_DIR,
        f"length{LENGTH_TYPE}",
        f"{case_id}.json"
    )

    try:
        if os.path.exists(result_json):
            os.remove(result_json)
            logger.info(f"✓ Cleaned up {result_json}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {result_json}: {str(e)}")

def append_to_master_csv(case_result, logger):
    """Append case result to master CSV immediately (incremental save)"""
    if not case_result:
        return False

    master_csv = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        PREDICT_DIR,
        f"master_results_{LENGTH_TYPE}.csv"
    )

    try:
        os.makedirs(os.path.dirname(master_csv), exist_ok=True)

        # Check if file exists and has content
        file_exists = os.path.exists(master_csv) and os.path.getsize(master_csv) > 0

        with open(master_csv, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=case_result.keys())
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            writer.writerow(case_result)

        return True
    except Exception as e:
        logger.warning(f"Could not append to master CSV: {str(e)}")
        return False

def get_case_result_from_evaluator(case_num, logger):
    """Extract case result from evaluator's temporary CSV (per-length to avoid conflicts)"""
    case_id = f"length{LENGTH_TYPE}_{case_num}"

    # Use per-length temporary file to avoid parallel write conflicts
    csv_file = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        PREDICT_DIR,
        f"case_by_case_summary_length{LENGTH_TYPE}.csv"
    )

    try:
        if os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('case_id') == case_id:
                        return row
    except Exception as e:
        logger.warning(f"Could not read results for {case_id}: {str(e)}")

    return None

def process_case(case_num, logger):
    """Process a single case: run, evaluate, and cleanup"""
    case_id = f"length{LENGTH_TYPE}_{case_num}"
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing case {case_num}: {case_id}")
    logger.info(f"{'='*60}")

    # Step 1: Run main.py for this case
    main_cmd = [
        "python3", "-m", "src.main",
        "--base_path", BASE_PATH,
        "--data_type", DATA_TYPE,
        "--result_dir", RESULT_DIR,
        "--length_type", str(LENGTH_TYPE),
        "--start_num", str(case_num),
        "--end_num", str(case_num + 1),
        "--log_path", os.path.join(LOG_DIR, f"mcts_{case_id}.txt"),
        "--model_name", MODEL_NAME
    ]

    if not run_command(main_cmd, f"MCTS for {case_id}", logger):
        logger.error(f"✗ MCTS execution failed for {case_id}")
        return None

    # Step 2: Run evaluator for this case
    eval_cmd = [
        "python3", "src/utils/evaluator.py",
        "--json_folder", RESULT_DIR,
        "--data_folder", BASE_PATH,
        "--output_base", PREDICT_DIR,
        "--length_types", str(LENGTH_TYPE),
        "--start_num", str(case_num),
        "--end_num", str(case_num + 1),
        "--data_type", DATA_TYPE,
        "--model_name", MODEL_NAME,
        "--validation", VALIDATION
    ]

    if not run_command(eval_cmd, f"Evaluation for {case_id}", logger):
        logger.error(f"✗ Evaluation failed for {case_id}")
        return None

    # Step 3: Rename evaluator's CSV to per-length name to avoid parallel write conflicts
    generic_csv = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        PREDICT_DIR,
        "case_by_case_summary.csv"
    )
    length_specific_csv = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        PREDICT_DIR,
        f"case_by_case_summary_length{LENGTH_TYPE}.csv"
    )
    try:
        if os.path.exists(generic_csv):
            shutil.move(generic_csv, length_specific_csv)
    except Exception as e:
        logger.warning(f"Could not rename temporary CSV: {str(e)}")

    # Step 4: Get result from evaluator's temporary CSV
    result = get_case_result_from_evaluator(case_num, logger)
    if not result:
        logger.error(f"✗ Could not read result for {case_id}")
        return None

    # Step 5: Append to master CSV immediately (incremental save for crash protection)
    if not append_to_master_csv(result, logger):
        logger.error(f"✗ Could not save result to master CSV for {case_id}")
        return None

    # Step 6: Cleanup intermediate results
    cleanup_case_results(case_id, logger)

    logger.info(f"✓ Successfully completed {case_id}")
    return result

def main(length_type=LENGTH_TYPE, start_num=START_NUM, end_num=END_NUM,
         base_path=BASE_PATH, result_dir=RESULT_DIR, predict_dir=PREDICT_DIR,
         validation=VALIDATION, cleanup_results=CLEANUP_RESULTS,
         model_name=MODEL_NAME, cases=CASES):
    global LENGTH_TYPE, START_NUM, END_NUM, BASE_PATH, RESULT_DIR, PREDICT_DIR, VALIDATION, CLEANUP_RESULTS, MODEL_NAME, CASES
    LENGTH_TYPE = length_type
    START_NUM = start_num
    END_NUM = end_num
    BASE_PATH = base_path
    RESULT_DIR = result_dir
    PREDICT_DIR = predict_dir
    VALIDATION = validation
    CLEANUP_RESULTS = cleanup_results
    MODEL_NAME = model_name
    CASES = cases

    logger, log_file = setup_logging()
    logger.info(f"Starting iterative case processing")
    case_list = CASES if CASES else list(range(START_NUM, END_NUM))
    logger.info(f"Cases: {case_list if CASES else f'{START_NUM}-{END_NUM}'}, Length type: {LENGTH_TYPE}, Model: {MODEL_NAME}")
    logger.info(f"Log file: {log_file}")

    successful_cases = []
    failed_cases = []

    # Process each case (results saved incrementally to master CSV)
    for case_num in case_list:
        try:
            result = process_case(case_num, logger)
            if result:
                successful_cases.append(case_num)
            else:
                failed_cases.append(case_num)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error processing case {case_num}: {str(e)}")
            failed_cases.append(case_num)

    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing complete!")
    logger.info(f"Successful: {len(successful_cases)} cases")
    logger.info(f"Failed: {len(failed_cases)} cases")
    if failed_cases:
        logger.info(f"Failed case numbers: {failed_cases}")
    logger.info(f"{'='*60}")

    # Results already saved incrementally to master CSV
    master_csv = os.path.join(
        "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
        PREDICT_DIR,
        f"master_results_{LENGTH_TYPE}.csv"
    )
    if os.path.exists(master_csv):
        with open(master_csv, 'r') as f:
            rows = len(f.readlines()) - 1  # Subtract header
        logger.info(f"✓ Master CSV saved to: {master_csv}")
        logger.info(f"✓ Total rows: {rows}")

        # Auto-archive results to safe location
        archive_dir = os.path.join(
            "/home/asurite.ad.asu.edu/jrtandel/transchema/BAT",
            "results_archive"
        )
        os.makedirs(archive_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"master_results_github-pipelines_length{LENGTH_TYPE}_{timestamp}.csv"
        latest_name = f"master_results_github-pipelines_length{LENGTH_TYPE}_latest.csv"

        archive_path = os.path.join(archive_dir, archive_name)
        latest_path = os.path.join(archive_dir, latest_name)

        try:
            shutil.copy(master_csv, archive_path)
            shutil.copy(master_csv, latest_path)
            logger.info(f"✓ Archived to: {archive_path}")
            logger.info(f"✓ Latest link: {latest_path}")
        except Exception as e:
            logger.warning(f"Failed to archive results: {str(e)}")

    logger.info("Done!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run MCTS cases iteratively with evaluation")
    parser.add_argument("--length_type", type=int, default=LENGTH_TYPE, help="Length type to process (default: 1)")
    parser.add_argument("--start_num", type=int, default=START_NUM, help="Start case number (default: 0)")
    parser.add_argument("--end_num", type=int, default=END_NUM, help="End case number (default: 100)")
    parser.add_argument("--base_path", type=str, default=BASE_PATH, help="Base path to benchmark data")
    parser.add_argument("--result_dir", type=str, default=RESULT_DIR, help="Result directory")
    parser.add_argument("--predict_dir", type=str, default=PREDICT_DIR, help="Prediction/evaluation directory")
    parser.add_argument("--validation", type=str, choices=["hard_match", "autopipeline"], default=VALIDATION,
                         help="Validation strategy passed to the evaluator (default: hard_match).")
    parser.add_argument("--no_cleanup", action="store_true",
                         help="Keep the intermediate per-case result JSON files instead of deleting them after evaluation.")
    parser.add_argument("--model_name", type=str, default=MODEL_NAME,
                         help="Model to use for MCTS generation and cost lookup; must be a key in BAT/src/llm/config.py's MODELS dict (e.g. o4-mini).")
    parser.add_argument("--cases", nargs='+', type=int, default=None,
                         help="Explicit list of case numbers to process (e.g. specific failed cases to retry), overriding --start_num/--end_num.")
    args = parser.parse_args()

    main(
        length_type=args.length_type,
        start_num=args.start_num,
        end_num=args.end_num,
        base_path=args.base_path,
        result_dir=args.result_dir,
        predict_dir=args.predict_dir,
        validation=args.validation,
        cleanup_results=not args.no_cleanup,
        model_name=args.model_name,
        cases=args.cases
    )
