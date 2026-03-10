"""
Launch script for DataMorpher RL fine-tuning.

Usage:
  # From the AgentFlow/ directory:
  python train/train_datamorpheragent.py

  # With per-run overrides (passed through to agentflow.verl as Hydra args):
  python train/train_datamorpheragent.py trainer.total_epochs=10 data.train_batch_size=32

Steps performed:
  1. (Optional) Prepare training data if parquet files don't exist yet.
  2. Set environment variables from datamorpherconfig.yaml.
  3. Start the rollout server  (python train/datamorpherrollout.py)  in a background process.
  4. Launch the verl PPO/GRPO trainer  (python -m agentflow.verl).
"""

import os
import sys
import yaml
import time
import signal
import argparse
import subprocess
from pathlib import Path


CONFIG_FILE = "train/datamorpherconfig.yaml"
ROLLOUT_SCRIPT = "train/datamorpherrollout.py"
DATA_PREP_SCRIPT = "train/prepare_rl_data.py"


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = yaml.safe_load(f)
    if config is None:
        raise ValueError(f"Empty or invalid YAML: {config_path}")
    return config


def set_env_vars(env_section: dict):
    print("Setting environment variables...")
    for key, value in env_section.items():
        os.environ[key] = str(value)
        print(f"  {key}={value}")


def maybe_prepare_data(config: dict):
    """
    Run prepare_rl_data.py if the parquet files don't exist yet.
    Reads BASE_DATA_DIR from config env to resolve the expected paths.
    """
    base_data_dir = os.path.expandvars(
        config.get("env", {}).get("BASE_DATA_DIR", "train/data")
    )
    train_parquet = os.path.join(base_data_dir, "train", "datamorphertrain.parquet")
    val_parquet = os.path.join(base_data_dir, "val", "datamorpherval.parquet")

    if os.path.exists(train_parquet) and os.path.exists(val_parquet):
        print(f"Parquet files already exist — skipping data preparation.")
        print(f"  train: {train_parquet}")
        print(f"  val:   {val_parquet}")
        return

    print("Parquet files not found. Running prepare_rl_data.py ...")
    result = subprocess.run(
        [
            sys.executable,
            DATA_PREP_SCRIPT,
            "--output_train", train_parquet,
            "--output_val", val_parquet,
        ],
        check=True,
        env=os.environ,
    )
    if result.returncode != 0:
        print("ERROR: Data preparation failed.")
        sys.exit(result.returncode)
    print("Data preparation complete.")


def build_verl_command(python_args: dict, overrides: list) -> list:
    command = [sys.executable, "-m", "agentflow.verl"]
    for key, value in python_args.items():
        if isinstance(value, str):
            expanded = os.path.expandvars(value)
            command.append(f"{key}={expanded}")
        else:
            command.append(f"{key}={value}")
    command.extend(overrides)
    return command


def main():
    parser = argparse.ArgumentParser(
        description="Launch DataMorpher RL fine-tuning (rollout server + verl trainer)."
    )
    parser.add_argument(
        "--config",
        default=CONFIG_FILE,
        help=f"Path to config YAML (default: {CONFIG_FILE})",
    )
    parser.add_argument(
        "--skip_data_prep",
        action="store_true",
        help="Skip automatic data preparation even if parquet files are missing.",
    )
    # Any remaining args are forwarded to agentflow.verl as Hydra overrides
    args, overrides = parser.parse_known_args()

    # ------------------------------------------------------------------ #
    # 1. Load config
    # ------------------------------------------------------------------ #
    print(f"\n{'='*60}")
    print(f"  DataMorpher RL Fine-Tuning")
    print(f"  Config: {args.config}")
    print(f"{'='*60}\n")

    config = load_config(args.config)

    # ------------------------------------------------------------------ #
    # 2. Set environment variables
    # ------------------------------------------------------------------ #
    set_env_vars(config.get("env", {}))

    # ------------------------------------------------------------------ #
    # 3. Prepare data (if needed)
    # ------------------------------------------------------------------ #
    if not args.skip_data_prep:
        maybe_prepare_data(config)

    # ------------------------------------------------------------------ #
    # 4. Start rollout server in background
    # ------------------------------------------------------------------ #
    agentflow_port = config.get("python_args", {}).get("agentflow.port", 9999)
    print(f"\nStarting DataMorpher rollout server on port {agentflow_port} ...")
    rollout_proc = subprocess.Popen(
        [sys.executable, ROLLOUT_SCRIPT],
        env=os.environ,
    )
    print(f"  Rollout server PID: {rollout_proc.pid}")

    # Give the rollout server a moment to bind its port before the trainer connects
    time.sleep(5)

    # ------------------------------------------------------------------ #
    # 5. Launch verl trainer
    # ------------------------------------------------------------------ #
    command = build_verl_command(config.get("python_args", {}), overrides)

    print(f"\nLaunching verl trainer:")
    print("  " + " ".join(str(c) for c in command))
    print("-" * 60)

    trainer_proc = None
    try:
        trainer_proc = subprocess.run(command, check=True, env=os.environ)
    except subprocess.CalledProcessError as exc:
        print(f"\nERROR: verl trainer exited with code {exc.returncode}")
        sys.exit(exc.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        # Cleanly terminate the rollout server
        if rollout_proc and rollout_proc.poll() is None:
            print(f"\nShutting down rollout server (PID {rollout_proc.pid}) ...")
            rollout_proc.send_signal(signal.SIGTERM)
            try:
                rollout_proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                rollout_proc.kill()
            print("Rollout server stopped.")

    print("\nTraining complete.")


if __name__ == "__main__":
    main()
