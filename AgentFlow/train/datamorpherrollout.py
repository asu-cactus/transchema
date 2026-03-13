"""
DataMorpher-specific RL rollout for fine-tuning Qwen2.5-7B-Instruct.

Replaces the LLM-judge reward in rollout.py with a deterministic pipeline
validator:  compare_lists_matching() → True/False → 1.0 / 0.0

Key differences from rollout.py:
  - eval_pipeline() uses validation/hard_match.py instead of gpt-4o
  - _solve_and_evaluate() extracts Python code (not a short text answer)
  - construct_solver is configured for DataMorpher pipeline tools
  - task["extra_info"] carries test_csv_paths and target_csv_path
"""

import os
import re
import sys
import json
import uuid
import asyncio
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from filelock import FileLock

from agentflow import Trainer, LitAgent, NamedResources, LLM, reward, configure_logger

# Compatibility shim:
# Some environments install the outer `agentflow` package (Trainer/LitAgent/etc.)
# but keep solver under `agentflow.agentflow.solver` with inner absolute imports
# like `agentflow.models.*`. We alias these namespaces before importing solver.
try:
    from agentflow.solver import construct_solver
except ModuleNotFoundError:
    import agentflow.agentflow.models as _af_models
    import agentflow.agentflow.engine as _af_engine
    import agentflow.agentflow.tools as _af_tools

    sys.modules.setdefault("agentflow.models", _af_models)
    sys.modules.setdefault("agentflow.engine", _af_engine)
    sys.modules.setdefault("agentflow.tools", _af_tools)

    from agentflow.agentflow.solver import construct_solver

configure_logger()

# ---------------------------------------------------------------------------
# Path setup so validation/ and eval_score/ are importable
# ---------------------------------------------------------------------------
_AGENTFLOW_ROOT = str(Path(__file__).resolve().parents[1])
if _AGENTFLOW_ROOT not in sys.path:
    sys.path.insert(0, _AGENTFLOW_ROOT)

_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

_EVAL_SCORE_ROOT = os.path.join(_REPO_ROOT, "eval_score")
if _EVAL_SCORE_ROOT not in sys.path:
    sys.path.insert(0, _EVAL_SCORE_ROOT)

from validation.hard_match import compare_lists_matching  # noqa: E402
import pandas as pd  # noqa: E402


# ---------------------------------------------------------------------------
# Reward function — deterministic CSV validator
# ---------------------------------------------------------------------------

@reward
async def eval_pipeline(
    generated_code: str,
    test_csv_paths: list,
    target_csv_path: str,
) -> float:
    """
    Executes the generated Python pipeline on the real test CSVs and scores the
    output against the ground-truth target.csv.

    Returns 1.0 if compare_lists_matching reports an exact match, else 0.0.
    Falls back to 0.0 on any execution or IO error.
    """
    if not generated_code or not generated_code.strip():
        return 0.0

    # ------------------------------------------------------------------ #
    # Patch the generated code so it reads from the correct test CSV paths
    # and writes to a known temp output file.
    # ------------------------------------------------------------------ #
    with tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False, prefix="dm_out_"
    ) as tmp_out:
        output_csv_path = tmp_out.name

    patched_code = _patch_code_paths(generated_code, test_csv_paths, output_csv_path)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, prefix="dm_script_"
    ) as tmp_script:
        tmp_script.write(patched_code)
        tmp_script_path = tmp_script.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_script_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("[eval_pipeline] Script timed out.")
        return 0.0
    except Exception as exc:
        print(f"[eval_pipeline] Subprocess error: {exc}")
        return 0.0
    finally:
        try:
            os.unlink(tmp_script_path)
        except OSError:
            pass

    if result.returncode != 0:
        print(f"[eval_pipeline] Script failed (exit {result.returncode}):\n{result.stderr[:400]}")
        return 0.0

    if not os.path.exists(output_csv_path) or os.path.getsize(output_csv_path) == 0:
        print("[eval_pipeline] Script produced no output CSV.")
        return 0.0

    try:
        output_df = pd.read_csv(output_csv_path)
        target_df = pd.read_csv(target_csv_path)
    except Exception as exc:
        print(f"[eval_pipeline] CSV read error: {exc}")
        return 0.0
    finally:
        try:
            os.unlink(output_csv_path)
        except OSError:
            pass

    try:
        avg_sim, is_correct, _sims, _matched = compare_lists_matching(output_df, target_df)
    except Exception as exc:
        print(f"[eval_pipeline] compare_lists_matching error: {exc}")
        return 0.0

    score = 1.0 if is_correct else float(avg_sim) if avg_sim is not None else 0.0
    print(f"[eval_pipeline] avg_sim={avg_sim:.4f}  exact_match={is_correct}  reward={score}")
    return score


def _patch_code_paths(code: str, test_csv_paths: list, output_csv_path: str) -> str:
    """
    Replace relative/placeholder CSV paths in generated code with absolute paths.

    Strategy:
      1. Replace any string matching  test_<digit>.csv  with the corresponding absolute path.
      2. Replace the last .to_csv("...") path with output_csv_path.
    """
    # Replace test_N.csv references
    for i, tp in enumerate(test_csv_paths):
        code = re.sub(
            rf'(["\'])([^"\']*\btest_{i}\.csv)\1',
            lambda m, p=tp: f'"{p}"',
            code,
        )

    # Replace output path in .to_csv(...)
    def replace_output(m):
        return f'.to_csv("{output_csv_path}"'

    code = re.sub(r'\.to_csv\s*\(\s*["\'][^"\']+\.csv["\']', replace_output, code)

    # If index=False is not in the to_csv call, keep as-is (don't break existing args)
    return code


def _extract_python_code(text: str) -> Optional[str]:
    """
    Extract a Python code block from the LLM output.

    Looks for ```python ... ``` first, then ``` ... ```, then falls back to
    returning the whole string if it starts with 'import'.
    """
    # Fenced python block
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Generic fenced block
    m = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if m:
        candidate = m.group(1).strip()
        if "import" in candidate or "pd." in candidate:
            return candidate

    # Raw code (no fences) starting with import
    stripped = text.strip()
    if stripped.startswith("import") or stripped.startswith("from "):
        return stripped

    return None


def _normalize_and_validate_task_payload(task: Any) -> dict:
    """
    Validate rollout task payload strictly.

    Fail fast on malformed tasks so training crashes with a clear root cause
    instead of silently producing empty/invalid batches later.
    """
    if not isinstance(task, dict):
        raise RuntimeError(f"Task is not a dict: got {type(task)}")

    task_id = task.get("id", "unknown")
    question = task.get("question", "")
    if not isinstance(question, str) or not question.strip():
        raise RuntimeError(f"[task_id={task_id}] Empty or missing 'question'.")

    extra_info = task.get("extra_info", {})
    if isinstance(extra_info, str):
        try:
            extra_info = json.loads(extra_info)
        except Exception as exc:
            raise RuntimeError(
                f"[task_id={task_id}] extra_info is invalid JSON: {exc}"
            ) from exc
    if not isinstance(extra_info, dict):
        raise RuntimeError(
            f"[task_id={task_id}] extra_info must be dict, got {type(extra_info)}"
        )

    test_csv_paths = extra_info.get("test_csv_paths", [])
    if not isinstance(test_csv_paths, list) or len(test_csv_paths) == 0:
        raise RuntimeError(
            f"[task_id={task_id}] Missing/empty extra_info.test_csv_paths"
        )
    for p in test_csv_paths:
        if not isinstance(p, str) or not p.strip():
            raise RuntimeError(
                f"[task_id={task_id}] test_csv_paths contains invalid entry: {p!r}"
            )
        if not os.path.exists(p):
            raise RuntimeError(f"[task_id={task_id}] test CSV does not exist: {p}")

    target_csv_path = extra_info.get("target_csv_path", task.get("result", ""))
    if not isinstance(target_csv_path, str) or not target_csv_path.strip():
        raise RuntimeError(
            f"[task_id={task_id}] Missing target CSV path in extra_info.target_csv_path/result"
        )
    if not os.path.exists(target_csv_path):
        raise RuntimeError(
            f"[task_id={task_id}] target CSV does not exist: {target_csv_path}"
        )

    return {
        "task_id": task_id,
        "question": question.strip(),
        "extra_info": extra_info,
        "test_csv_paths": test_csv_paths,
        "target_csv_path": target_csv_path,
    }


# ---------------------------------------------------------------------------
# AgentFlowRollout — wraps construct_solver for DataMorpher
# ---------------------------------------------------------------------------

class DataMorpherAgentRollout:
    def __init__(
        self,
        resources: NamedResources,
        llm_engine_name: str = "Qwen/Qwen2.5-7B-Instruct",
        model_engine: list = None,
        tool_engine: list = None,
        max_steps: int = 3,
        max_time: int = 500,
        max_tokens: int = 4096,
        base_url: str = "http://localhost:8888",
        verbose: bool = True,
        temperature: float = 0.0,
    ):
        if model_engine is None:
            model_engine = ["trainable", "trainable", "trainable", "trainable"]
        if tool_engine is None:
            tool_engine = ["Default"]

        # Resolve the correct vLLM proxy URL.
        # Priority (highest first):
        #  1. AGENTFLOW_VLLM_BASE_URL env var (explicit override)
        #  2. Constructor base_url if it looks valid (comes from resources.get("main_llm").endpoint)
        #  3. URL file written by daemon (/tmp/agentflow_vllm_url.txt) — fallback only
        #  4. Whatever was in constructor base_url as last resort
        _default_base = "http://localhost:8888"
        env_base_url = os.environ.get("AGENTFLOW_VLLM_BASE_URL", "").strip()
        if env_base_url:
            base_url = env_base_url
            print(f"  [DataMorpherAgentRollout] base_url from env var: {base_url}")
        elif base_url and base_url != _default_base:
            # Caller passed a real URL (from resources) — use it directly.
            print(f"  [DataMorpherAgentRollout] base_url from resources: {base_url}")
        else:
            # No valid URL from caller; try the URL file as fallback.
            vllm_url_file = os.environ.get(
                "AGENTFLOW_VLLM_URL_FILE", "/tmp/agentflow_vllm_url.txt"
            )
            try:
                with open(vllm_url_file) as fh:
                    file_url = fh.read().strip()
                if file_url:
                    base_url = file_url
                    print(f"  [DataMorpherAgentRollout] base_url from URL file: {base_url}")
            except Exception:
                pass
        print(f"****** DataMorpher solver: model={llm_engine_name}  base_url={base_url} ******")

        prefix = "" if "gpt" in llm_engine_name else "vllm-"
        self.solver = construct_solver(
            llm_engine_name=prefix + llm_engine_name,
            enabled_tools=[
                "Configure_Join_Operator_Tool",
                "Configure_Union_Operator_Tool",
                "Configure_GroupBy_Aggregate_Operator_Tool",
                "Add_Pivot_Tool",
                "Add_Unpivot_Tool",
                "Code_Gen_And_Score_Tool",
                "Critique_Pipeline_Tool",
            ],
            tool_engine=tool_engine,
            model_engine=model_engine,
            output_types="final",
            max_steps=max_steps,
            max_time=max_time,
            max_tokens=max_tokens,
            base_url=base_url,
            verbose=verbose,
            temperature=temperature,
            execute_pipeline=True,
        )
        # Forcibly cap max_tokens on every LLM engine attached to the planner/verifier.
        # This works regardless of which version of the agentflow package is loaded in
        # memory (editable install, cached bytecode, or old Ray worker).
        _safe_max = min(max_tokens, 1024)
        for _component_name in ("planner", "verifier"):
            _component = getattr(self.solver, _component_name, None)
            if _component is None:
                continue
            if hasattr(_component, "max_tokens"):
                _component.max_tokens = _safe_max
            for _engine_attr in ("llm_engine", "llm_engine_fixed"):
                _engine = getattr(_component, _engine_attr, None)
                if _engine is None:
                    continue
                # Works with new vllm.py (has default_max_tokens attribute).
                _engine.default_max_tokens = _safe_max
                # Belt-and-suspenders: patch _generate_text if it still has the
                # hardcoded 2048 default (old vllm.py in a stale Ray worker).
                import functools, inspect
                try:
                    sig = inspect.signature(_engine._generate_text)
                    if sig.parameters.get("max_tokens") is not None:
                        _orig = _engine._generate_text
                        @functools.wraps(_orig)
                        def _capped_generate_text(_orig=_orig, _safe=_safe_max,
                                                  *args, **kwargs):
                            if "max_tokens" not in kwargs or kwargs["max_tokens"] is None:
                                kwargs["max_tokens"] = _safe
                            return _orig(*args, **kwargs)
                        _engine._generate_text = _capped_generate_text
                except Exception:
                    pass
        print(f"[DataMorpherAgentRollout] max_tokens capped to {_safe_max} on all planner engines")
        self.llm_engine = llm_engine_name
        self.verbose = verbose

    def solve(self, question: str, ground_truth_csv: str = None) -> dict:
        return self.solver.solve(question)


# ---------------------------------------------------------------------------
# Rollout (LitAgent subclass)
# ---------------------------------------------------------------------------

class DataMorpherRollout(LitAgent):

    def __init__(
        self,
        server_public_ip: str = "Default",
        exp_name: str = "datamorpheragent",
        rollout_n: int = 8,
        batch_size: int = 16,
        model_engine: list = None,
        tool_engine: list = None,
        max_steps: int = 3,
        max_tokens: int = 4096,
        train_temperature: float = 0.7,
        test_temperature: float = 0.0,
        timeout: int = 500,
    ):
        super().__init__()
        if model_engine is None:
            model_engine = ["trainable", "trainable", "trainable", "trainable"]
        if tool_engine is None:
            tool_engine = ["Default"]

        self.server_public_ip = server_public_ip
        self.exp_name = exp_name
        self.rollout_n = rollout_n
        self.train_batch_size = batch_size
        self.model_engine = model_engine
        self.tool_engine = tool_engine
        self.max_steps = max_steps
        self.max_tokens = max_tokens
        self.train_temperature = train_temperature
        self.test_temperature = test_temperature
        self.timeout = timeout

        self.training_agent: Optional[DataMorpherAgentRollout] = None
        self.validation_agent: Optional[DataMorpherAgentRollout] = None
        self.val_step_n: Optional[int] = None
        self._last_vllm_base_url: Optional[str] = None  # detect URL changes

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_dir = os.environ.get("ROLLOUT_DIR", f"./rollout_data/{self.server_public_ip}")
        self.base_rollout_dir = os.path.join(base_dir, f"{exp_name}_{timestamp}")
        self.rollout_dir: Optional[str] = None
        self.train_rollout_dir: Optional[str] = None
        self.val_rollout_dir: Optional[str] = None
        self.train_lock_file: Optional[str] = None
        self.val_lock_file: Optional[str] = None

        self.run_info_file = os.path.join(self.base_rollout_dir, ".run_info")
        self.init_lock_file = os.path.join(self.base_rollout_dir, ".init.lock")

    # ------------------------------------------------------------------ #
    # One-time initialisation (process-safe via filelock)
    # ------------------------------------------------------------------ #

    async def _initialize_run_once(self, resources: NamedResources):
        if self.rollout_dir is not None:
            return
        os.makedirs(self.base_rollout_dir, exist_ok=True)
        init_lock = FileLock(self.init_lock_file, timeout=50)
        with init_lock:
            if os.path.exists(self.run_info_file):
                with open(self.run_info_file) as f:
                    final_rollout_dir = f.read().strip()
            else:
                llm: LLM = resources.get("main_llm")
                model_name = llm.model.rsplit("/", 1)[-1]
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                final_rollout_dir = os.path.join(
                    self.base_rollout_dir, f"{model_name}_{ts}"
                )
                with open(self.run_info_file, "w") as f:
                    f.write(final_rollout_dir)

        self.rollout_dir = final_rollout_dir
        self.train_rollout_dir = os.path.join(self.rollout_dir, "train")
        self.val_rollout_dir = os.path.join(self.rollout_dir, "validation")
        os.makedirs(self.train_rollout_dir, exist_ok=True)
        os.makedirs(self.val_rollout_dir, exist_ok=True)
        self.train_lock_file = os.path.join(self.train_rollout_dir, ".train.lock")
        self.val_lock_file = os.path.join(self.val_rollout_dir, ".val.lock")

    # ------------------------------------------------------------------ #
    # Core solve + evaluate
    # ------------------------------------------------------------------ #

    async def _solve_and_evaluate(
        self,
        agent: DataMorpherAgentRollout,
        task: Any,
        step_n: int,
        val: bool = False,
    ):
        validated = _normalize_and_validate_task_payload(task)
        extra_info = validated["extra_info"]
        test_csv_paths: list = validated["test_csv_paths"]
        target_csv_path: str = validated["target_csv_path"]
        question: str = validated["question"]
        task_id: str = validated["task_id"]

        generated_code = None
        result = {}
        # Run the synchronous solver in a thread so it doesn't block the async event loop.
        # asyncio.wait_for enforces a hard wall-clock timeout regardless of internal hangs.
        solve_timeout = max(60, int(self.timeout) + 30)  # agent timeout + 30s buffer
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(agent.solve, question=question),
                timeout=float(solve_timeout),
            )

            # Extract Python code from solver output
            for key in ("final_output", "direct_output", "base_output"):
                raw = result.get(key, "")
                if raw:
                    code = _extract_python_code(str(raw))
                    if code:
                        generated_code = code
                        break

            if generated_code is None:
                print("[DataMorpherRollout] No Python code found in solver output.")
        except asyncio.TimeoutError:
            print(f"[DataMorpherRollout] Solver timed out after {solve_timeout}s — returning 0 reward.")
        except Exception as exc:
            print(f"[DataMorpherRollout] Solver error: {exc}")

        reward_value = await eval_pipeline(
            generated_code or "",
            test_csv_paths,
            target_csv_path,
        )

        idx = extra_info.get("idx", task.get("id", "unknown"))
        print(
            f"[DataMorpherRollout] id={task_id}  reward={reward_value}  "
            f"code_found={'yes' if generated_code else 'no'}"
        )

        rollout_data = {
            "step": step_n,
            "idx": idx,
            "id": task_id,
            "prompt": question,
            "model": agent.llm_engine,
            "target_csv": target_csv_path,
            "generated_code": generated_code or "",
            "reward": reward_value,
            "total_result": result,
            "timestamp": datetime.now().isoformat(),
        }

        save_dir = self.val_rollout_dir if val else self.train_rollout_dir
        step_dir = os.path.join(save_dir, f"step_{step_n}")
        idx_dir = os.path.join(step_dir, f"idx_{idx}")
        os.makedirs(idx_dir, exist_ok=True)

        json_count = sum(
            len([f for f in files if f.endswith(".json")])
            for _root, _dirs, files in os.walk(idx_dir)
        )
        if json_count >= self.rollout_n:
            print(
                f"[DataMorpherRollout] Skip save for idx {idx}: already have "
                f"{json_count}/{self.rollout_n} rollouts (stale directory from a prior run)."
            )
            return

        save_path = os.path.join(idx_dir, f"rollout_{uuid.uuid4()}.json")
        with open(save_path, "w") as f:
            json.dump(rollout_data, f, indent=2, default=str)
        print(f"[DataMorpherRollout] Saved rollout → {save_path}")

    # ------------------------------------------------------------------ #
    # LitAgent interface
    # ------------------------------------------------------------------ #

    async def training_rollout_async(
        self, task: Any, rollout_id: str, resources: NamedResources
    ) -> Any:
        await self._initialize_run_once(resources)

        llm: LLM = resources.get("main_llm")
        current_url = llm.endpoint
        if self.training_agent is None or current_url != self._last_vllm_base_url:
            if self.training_agent is not None:
                print(f"  [DataMorpherRollout] vLLM URL changed, recreating training agent: {current_url}")
            self.training_agent = DataMorpherAgentRollout(
                resources=resources,
                llm_engine_name=llm.model,
                model_engine=self.model_engine,
                tool_engine=self.tool_engine,
                max_steps=self.max_steps,
                max_tokens=self.max_tokens,
                base_url=current_url,
                verbose=True,
                temperature=self.train_temperature,
                max_time=self.timeout,
            )
            self._last_vllm_base_url = current_url

        lock = FileLock(self.train_lock_file, timeout=30)
        with lock:
            step_dirs = [
                d for d in os.listdir(self.train_rollout_dir) if d.startswith("step_")
            ]
            step_nums = [
                int(d.replace("step_", ""))
                for d in step_dirs
                if d.replace("step_", "").isdigit()
            ]
            current_step_n = max(step_nums) if step_nums else 1
            step_dir_path = os.path.join(self.train_rollout_dir, f"step_{current_step_n}")
            if os.path.exists(step_dir_path) and len(os.listdir(step_dir_path)) >= self.train_batch_size:
                current_step_n += 1
            step_n = current_step_n

        await self._solve_and_evaluate(self.training_agent, task, step_n, val=False)

    async def validation_rollout_async(
        self, task: Any, rollout_id: str, resources: NamedResources
    ) -> Any:
        await self._initialize_run_once(resources)

        val_lock = FileLock(self.val_lock_file, timeout=50)
        with val_lock:
            llm: LLM = resources.get("main_llm")
            current_url = llm.endpoint
            if self.validation_agent is None or current_url != self._last_vllm_base_url:
                self.validation_agent = DataMorpherAgentRollout(
                    resources=resources,
                    llm_engine_name=llm.model,
                    model_engine=self.model_engine,
                    tool_engine=self.tool_engine,
                    max_steps=self.max_steps,
                    max_tokens=self.max_tokens,
                    base_url=current_url,
                    verbose=True,
                    temperature=self.test_temperature,
                    max_time=self.timeout,
                )
                self._last_vllm_base_url = current_url

            train_step_dirs = [
                d for d in os.listdir(self.train_rollout_dir) if d.startswith("step_")
            ]
            train_step_nums = [
                int(d.replace("step_", ""))
                for d in train_step_dirs
                if d.replace("step_", "").isdigit()
            ]
            self.val_step_n = max(train_step_nums) if train_step_nums else 0

        await self._solve_and_evaluate(self.validation_agent, task, self.val_step_n, val=True)


# ---------------------------------------------------------------------------
# Entry point (mirrors rollout.py __main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        from util.parse_config import get_values_from_yaml
        from util.port_cleanup import kill_process_on_port
        from util.get_pub_ip import get_public_ip_with_fallback
    except ModuleNotFoundError:
        # Fallback for environments where AgentFlow root is imported as a package.
        from AgentFlow.util.parse_config import get_values_from_yaml
        from AgentFlow.util.port_cleanup import kill_process_on_port
        from AgentFlow.util.get_pub_ip import get_public_ip_with_fallback
    from pprint import pprint

    server_public_ip = get_public_ip_with_fallback()

    keys_to_retrieve = [
        "EXPERIMENT_NAME",
        "data.train_batch_size",
        "actor_rollout_ref.rollout.n",
        "agentflow.port",
        "N_WORKERS",
        "MODEL_ENGINE",
        "TOOL_ENGINE",
        "TOOL_STEPS",
        "TRAIN_TEMPERATURE",
        "TEST_TEMPERATURE",
        "data.max_response_length",
        "AGENT_MAX_TIMEOUT",
    ]

    config_file = "train/datamorpherconfig.yaml"
    values = get_values_from_yaml(config_file, keys_to_retrieve)

    config_keys_map = {
        "EXPERIMENT_NAME": "exp_name",
        "data.train_batch_size": "batch_size",
        "actor_rollout_ref.rollout.n": "rollout_n",
        "agentflow.port": "port",
        "N_WORKERS": "n_workers",
        "MODEL_ENGINE": "model_engine",
        "TOOL_ENGINE": "tool_engine",
        "TOOL_STEPS": "max_steps",
        "TRAIN_TEMPERATURE": "train_temperature",
        "TEST_TEMPERATURE": "test_temperature",
        "data.max_response_length": "max_tokens",
        "AGENT_MAX_TIMEOUT": "timeout",
    }

    config_dict = dict(zip(config_keys_map.values(), values))

    # Smoke mode: aggressively reduce per-task latency so hangs surface quickly.
    if os.environ.get("AGENTFLOW_SMOKE_MODE", "0") == "1":
        config_dict["timeout"] = min(int(config_dict.get("timeout", 500)), 60)
        config_dict["max_steps"] = 1
        config_dict["rollout_n"] = 1
        config_dict["train_temperature"] = 0.0
        config_dict["test_temperature"] = 0.0
        # Reduce max_tokens so prompt+completion stays within vLLM max_model_len.
        # vLLM context window = max_prompt_length + max_response_length = 4608 in smoke.
        # Prompts can be 3000+ tokens; cap completion at 512 to stay within budget.
        config_dict["max_tokens"] = min(int(config_dict.get("max_tokens", 512)), 512)
        print(
            "Smoke-mode rollout overrides => "
            f"timeout={config_dict['timeout']}, "
            f"max_steps={config_dict['max_steps']}, "
            f"rollout_n={config_dict['rollout_n']}, "
            f"train_temperature={config_dict['train_temperature']}, "
            f"test_temperature={config_dict['test_temperature']}"
        )

    port_to_use = config_dict.get("port")
    if port_to_use:
        kill_process_on_port(port_to_use)

    print("DataMorpher agent params:")
    pprint(config_dict, indent=2, width=80, compact=True)

    trainer = Trainer(n_workers=config_dict["n_workers"])
    agent = DataMorpherRollout(
        server_public_ip=server_public_ip,
        **{
            k: v
            for k, v in config_dict.items()
            if k not in ("n_workers", "port")
        },
    )
    trainer.fit(agent, f"http://localhost:{config_dict['port']}/")
