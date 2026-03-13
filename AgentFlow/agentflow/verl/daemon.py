import asyncio
import json
import logging
import os
import random
import socket
import threading
import time
import uuid
from typing import Dict, List, Optional

import numpy as np
import requests
import torch
from agentflow import LLM, AgentFlowServer, NamedResources, Rollout, configure_logger
from flask import Flask, Response, abort, request
from openai.types.chat.chat_completion import ChatCompletion
from tensordict import TensorDict

from verl import DataProto

configure_logger()

logger = logging.getLogger(__name__)


def get_left_padded_ids_and_attention_mask(ids: List[int], max_length: int, pad_token_id: int):
    """
    Left-pad (or truncate) a sequence of token IDs to a fixed length,
    and build the corresponding attention mask.

    Args:
        ids:             the original list of token IDs.
        max_length:      desired total length after padding/truncation.
        pad_token_id:    ID to use for padding.

    Returns:
        padded_ids (any):      list of length == max_length.
        attention_mask (any):  list of same length: 1 for non-pad tokens, 0 for pads.
    """
    seq_len = len(ids)

    if seq_len >= max_length:
        # too long → truncate from the left, keep the last max_length tokens
        trimmed = ids[-max_length:]
        attention_mask = [1] * max_length
        return trimmed, attention_mask

    # too short → pad on the left
    pad_len = max_length - seq_len
    padded_ids = [pad_token_id] * pad_len + ids
    attention_mask = [0] * pad_len + [1] * seq_len
    return padded_ids, attention_mask


def get_right_padded_ids_and_attention_mask(ids: List[int], max_length: int, pad_token_id: int):
    """
    Right-pad (or truncate) a sequence of token IDs to a fixed length,
    and build the corresponding attention mask.

    Args:
        ids:            the original list of token IDs.
        max_length:     desired total length after padding/truncation.
        pad_token_id:   ID to use for padding.

    Returns:
        padded_ids (any):     list of length == max_length.
        attention_mask (any): list of same length: 1 for non-pad tokens, 0 for pads.
    """
    seq_len = len(ids)

    if seq_len >= max_length:
        # too long → truncate to the first max_length tokens
        trimmed = ids[:max_length]
        attention_mask = [1] * max_length
        return trimmed, attention_mask

    # too short → pad on the right
    pad_len = max_length - seq_len
    padded_ids = ids + [pad_token_id] * pad_len
    attention_mask = [1] * seq_len + [0] * pad_len
    return padded_ids, attention_mask


def _find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class AgentModeDaemon:
    """
    AgentModeDaemon using the AgentFlowServer SDK.

    This class manages the server lifecycle, task queueing, and results
    retrieval, while also running a proxy server for LLM requests. It maintains
    the original interface for compatibility with the RayPPOTrainer.
    """

    def __init__(
        self,
        port,
        train_rollout_n,
        train_information,
        tokenizer,
        mini_batch_size,
        pad_token_id,
        reward_fillna_value=0.0,
        llm_timeout_seconds=600.0,
        enable_rollout_validation=True,
        max_empty_retries=2,
    ):
        # Server and Task Configuration
        self.server_port = port
        self.llm_timeout_seconds = llm_timeout_seconds
        self.server = AgentFlowServer(
            host="0.0.0.0", port=self.server_port, task_timeout_seconds=self.llm_timeout_seconds
        )
        self.proxy_port = _find_available_port()  # Run proxy on a different port

        # Training and Data Configuration
        self.train_rollout_n = train_rollout_n
        self.train_information = train_information
        self.mini_batch_size = mini_batch_size
        self.pad_token_id = pad_token_id
        self.tokenizer = tokenizer
        self.reward_fillna_value = reward_fillna_value

        # Internal State
        self.backend_llm_server_addresses: List[str] = []
        self._total_tasks_queued = 0
        self._completed_rollouts: Dict[str, Rollout] = {}
        self._task_id_to_original_sample: Dict[str, Dict] = {}
        self._server_thread: Optional[threading.Thread] = None
        self._proxy_thread: Optional[threading.Thread] = None
        self.is_train = True
        self._current_resources_id: Optional[str] = None

        self.enable_rollout_validation = enable_rollout_validation
        self.max_empty_retries = max_empty_retries
        self._empty_rollout_counts: Dict[str, int] = {}

    def _start_proxy_server(self):
        """
        Initializes and runs a Flask-based proxy server in a separate thread.
        This proxy load-balances requests to the actual backend LLM servers.
        """
        app = Flask(__name__)

        num_requests = 0
        last_request_time = 0

        @app.route("/v1/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        def proxy(path):
            if not self.backend_llm_server_addresses:
                abort(503, description="No backend LLM servers available.")

            # Randomly choose a backend server for load balancing
            target_server = random.choice(self.backend_llm_server_addresses)
            target_url = f"http://{target_server}/v1/{path}"

            # Copy client request headers, removing the Host header
            headers = {key: value for key, value in request.headers if key.lower() != "host"}

            # Log the request for debugging
            nonlocal num_requests, last_request_time
            current_time = time.time()
            num_requests += 1
            if current_time - last_request_time > 60 or num_requests == 1 or num_requests % 100 == 0:
                print(f"Proxying {request.method} request to {target_server}. Request data: {request.get_data()}")
            last_request_time = current_time

            try:
                # Forward the request to the target backend
                resp = requests.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=request.args,
                    data=request.get_data(),
                    cookies=request.cookies,
                    allow_redirects=False,
                    timeout=self.llm_timeout_seconds,
                )
                # Filter out hop-by-hop headers before returning the response
                excluded_headers = [
                    "content-encoding",
                    "content-length",
                    "transfer-encoding",
                    "connection",
                    "keep-alive",
                    "proxy-authenticate",
                    "proxy-authorization",
                    "te",
                    "trailers",
                    "upgrade",
                ]
                response_headers = [
                    (name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers
                ]
                if resp.status_code == 200:
                    response_json = json.loads(resp.content.decode("utf-8"))
                    replaced_return_content = json.dumps(response_json).encode("utf-8")
                    return Response(replaced_return_content, status=resp.status_code, headers=response_headers)
                return Response(resp.content, resp.status_code, response_headers)
            except requests.exceptions.RequestException as e:
                abort(500, description=f"Error proxying request: {e}")

        # Shared flag: Flask thread signals success/failure here.
        _proxy_ready = threading.Event()
        _proxy_error: list = [None]

        def run_app():
            try:
                app.run(host="0.0.0.0", port=self.proxy_port, threaded=True, debug=False)
            except Exception as exc:
                _proxy_error[0] = exc
                _proxy_ready.set()  # unblock the waiter so it can detect failure fast

        self._proxy_thread = threading.Thread(target=run_app, daemon=True)
        self._proxy_thread.start()

        # Wait until Flask is actually accepting connections before continuing.
        import socket as _sock
        proxy_up = False
        for _wait_i in range(60):  # up to 30 s
            if _proxy_error[0] is not None:
                break  # Flask crashed — stop waiting
            try:
                with _sock.create_connection(("127.0.0.1", self.proxy_port), timeout=1):
                    proxy_up = True
                    break
            except OSError:
                time.sleep(0.5)

        if _proxy_error[0] is not None:
            raise RuntimeError(
                f"[AgentModeDaemon] Flask proxy failed to start on port {self.proxy_port}: "
                f"{_proxy_error[0]}"
            )
        if not proxy_up:
            raise RuntimeError(
                f"[AgentModeDaemon] Flask proxy did not come up on port {self.proxy_port} "
                f"within 30 s. Port may be taken by a previous run — run 'ray stop --force' "
                f"and retry."
            )
        print(f"[AgentModeDaemon] Proxy server verified on port {self.proxy_port}")

    def _resolve_proxy_host_for_workers(self) -> str:
        """
        Resolve a worker-routable host for the local proxy server.

        Default: 127.0.0.1 (loopback), which works for single-node runs and
        avoids CHPC firewall rules that drop same-node traffic sent to the
        node's external IP.

        Multi-node: set AGENTFLOW_PROXY_HOST to the daemon node's routable IP
        so workers on other nodes can reach the proxy.
        """
        env_host = os.environ.get("AGENTFLOW_PROXY_HOST", "").strip()
        if env_host:
            return env_host
        # Default to loopback — always reachable from processes on the same node.
        return "127.0.0.1"

    def start(self):
        """Starts the main AgentFlowServer and the proxy server."""

        # Delete any stale URL file from a previous run so old ports can't mislead workers.
        vllm_url_file = os.environ.get("AGENTFLOW_VLLM_URL_FILE", "/tmp/agentflow_vllm_url.txt")
        try:
            os.remove(vllm_url_file)
            print(f"[AgentModeDaemon] Removed stale URL file: {vllm_url_file}")
        except FileNotFoundError:
            pass

        def run_server():
            """Run the AgentFlowServer in a separate thread."""
            asyncio.run(self.server.run_forever())

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

        # Wait for the server's internal startup event to be set.
        print("Waiting for AgentFlowServer to start...")
        is_ready = self.server.startup_event.wait(timeout=20.0)  # Wait up to 20s
        if not is_ready:
            raise RuntimeError("AgentFlowServer failed to start within the timeout period.")

        print(f"AgentFlowServer control plane running on port {self.server_port}")

        self._start_proxy_server()

        # Write proxy URL to the file immediately after the proxy is confirmed running.
        # This is the earliest possible time the URL is valid and can be used by workers.
        # _async_set_up will also write the URL, but this ensures it's available ASAP.
        early_proxy_url = f"http://127.0.0.1:{self.proxy_port}/v1"
        try:
            with open(vllm_url_file, "w") as _fh:
                _fh.write(early_proxy_url)
            print(f"[AgentModeDaemon] Proxy URL written to {vllm_url_file}: {early_proxy_url}")
        except Exception as _e:
            logger.warning(f"Could not write early proxy URL file: {_e}")

    async def _async_set_up(self, data, server_addresses, is_train=True):
        """Async helper to set up data and resources on the server."""
        self.clear_data_and_server()

        # Clear any orphaned rollouts from previous runs
        try:
            orphaned_rollouts = await self.server.retrieve_completed_rollouts()
            if orphaned_rollouts:
                logger.info(f"Cleared {len(orphaned_rollouts)} orphaned rollouts from previous runs")
        except Exception as e:
            logger.warning(f"Failed to clear orphaned rollouts: {e}")

        self.backend_llm_server_addresses = server_addresses
        self.is_train = is_train

        # 1. Update resources on the server for clients to use.
        #
        # Connect workers DIRECTLY to vLLM via loopback (127.0.0.1).  vLLM
        # listens on 0.0.0.0 so 127.0.0.1 always works from the same node,
        # avoids CHPC firewall rules that drop same-node traffic sent to the
        # node's external IP, and eliminates the Flask proxy as a failure point.
        #
        # For multi-node setups where workers run on a different node from vLLM,
        # set AGENTFLOW_VLLM_DIRECT_HOST to the routable vLLM node IP.
        if server_addresses:
            raw_addr = str(server_addresses[0])  # e.g. "10.242.160.83:8000"
            vllm_port = raw_addr.rsplit(":", 1)[-1] if ":" in raw_addr else "8000"
            direct_host = os.environ.get("AGENTFLOW_VLLM_DIRECT_HOST", "127.0.0.1").strip()
            llm_endpoint = f"http://{direct_host}:{vllm_port}/v1"
        else:
            llm_endpoint = f"http://127.0.0.1:{self.proxy_port}/v1"  # last-resort fallback

        logger.info(f"Using direct vLLM endpoint for rollout workers: {llm_endpoint}")
        print(f"[AgentModeDaemon] LLM endpoint for rollout workers: {llm_endpoint}")

        llm_resource = LLM(
            endpoint=llm_endpoint,
            model=self.train_information.get("model", "default-model"),
            sampling_parameters={"temperature": self.train_information.get("temperature", 0.7)},
        )
        logger.info(f"AgentModeDaemon LLM endpoint for workers: {llm_resource.endpoint}")
        print(f"[AgentModeDaemon] LLM resource created with endpoint: {llm_resource.endpoint}")

        # Write the resolved endpoint to a well-known file so solver sub-components
        # in the rollout subprocess can pick it up (os.environ doesn't cross processes).
        vllm_url_file = os.environ.get(
            "AGENTFLOW_VLLM_URL_FILE",
            "/tmp/agentflow_vllm_url.txt",
        )
        try:
            with open(vllm_url_file, "w") as fh:
                fh.write(llm_endpoint)
            logger.info(f"Wrote vLLM endpoint to {vllm_url_file}: {llm_endpoint}")
            print(f"[AgentModeDaemon] vLLM URL file written: {vllm_url_file} → {llm_endpoint}")
        except Exception as _e:
            logger.warning(f"Could not write vLLM URL file {vllm_url_file}: {_e}")
            print(f"[AgentModeDaemon] WARNING: Could not write vLLM URL file: {_e}")
        resources: NamedResources = {"main_llm": llm_resource}
        resources_id = await self.server.update_resources(resources)
        self._current_resources_id = resources_id

        # 2. Queue tasks for agents to process
        keys = list(data.keys())
        num_samples = len(data[keys[0]])
        rollouts_per_sample = self.train_rollout_n if is_train else 1

        print(f"Queueing {num_samples} samples with {rollouts_per_sample} rollouts each for {'training' if is_train else 'validation'}")

        for i in range(num_samples):
            data_id = str(uuid.uuid4())
            original_sample = {key: data[key][i] for key in keys}
            original_sample["data_id"] = data_id

            # For training, each sample is rolled out multiple times
            for j in range(rollouts_per_sample):
                task_metadata = {"data_id": data_id, "is_train": is_train}

                # Data ID is different from Rollout ID, as one data can have multiple rollouts.
                rollout_id = await self.server.queue_task(
                    sample=original_sample,
                    mode="train" if is_train else "val",
                    resources_id=resources_id,
                    metadata=task_metadata,
                )
                # Store original sample data to reconstruct batch information later
                self._task_id_to_original_sample[rollout_id] = original_sample
                self._total_tasks_queued += 1

        print(f"Total tasks queued: {self._total_tasks_queued}")

    def set_up_data_and_server(self, data, server_addresses, is_train=True):
        """Synchronous wrapper for setting up data and server resources."""
        if not self.server.loop or not self.server.startup_event.is_set():
            raise RuntimeError("Server is not running or ready.")

        coro = self._async_set_up(data, server_addresses, is_train)
        future = asyncio.run_coroutine_threadsafe(coro, self.server.loop)
        try:
            future.result(timeout=60)  # Wait for completion with a timeout
        except Exception as e:
            print(f"Failed to set up data on server: {e}")
            raise


    def save_response_token_ids(self, rollout: Rollout, save_path: str = "tmp.json"):
        """
        Extracts response token_ids from rollout.triplets and saves them to a JSON file.
        """
        print(f"[DEBUG] Saving response token_ids for rollout {rollout.rollout_id} -> {save_path}")
        import json
        from pathlib import Path

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        if rollout.triplets is None or len(rollout.triplets) == 0:
            print(f"Warning: No triplets to save for rollout {rollout.rollout_id}.")
            return
        
        response_token_ids = [r.response.get("token_ids", []) for r in rollout.triplets]
        response_texts = [self.tokenizer.decode(ids) for ids in response_token_ids]

        data = {
            "rollout_id": rollout.rollout_id,
            "response_token_ids": response_token_ids,
            "response": response_texts   # 这里是字符串形式
        }

        with open(save_path, "a", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_empty_response_prompt_token_ids(self, rollout: Rollout, save_path: str = "empty_response_prompts.json"):
        """
        Extracts prompt token_ids from rollout.triplets when response is empty and saves them to a JSON file.
        """
        print(f"[DEBUG] Saving empty response prompt token_ids for rollout {rollout.rollout_id} -> {save_path}")
        import json
        from pathlib import Path
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        if rollout.triplets is None or len(rollout.triplets) == 0:
            print(f"Warning: No triplets to save for rollout {rollout.rollout_id}.")
            return
        
        empty_response_prompts = []
        for r in rollout.triplets:
            if not r.response.get("token_ids", []):
                prompt_ids = r.prompt.get("token_ids", [])
                prompt_text = self.tokenizer.decode(prompt_ids)
                empty_response_prompts.append({
                    "prompt_token_ids": prompt_ids,
                    "prompt_text": prompt_text
                })
        
        if not empty_response_prompts:
            print(f"No empty responses found for rollout {rollout.rollout_id}.")
            return
        
        data = {
            "rollout_id": rollout.rollout_id,
            "empty_response_prompts": empty_response_prompts
        }
        
        with open(save_path, "a", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _validate_data(self, rollout: Rollout):
        """DEBUG: SAVE THE OUTPUT TRIPLES"""
        # self.save_response_token_ids(rollout, f"./triples/response/rollout_{rollout.rollout_id}.json")
        # self.save_empty_response_prompt_token_ids(rollout, f"./triples/empty_responses/rollout_{rollout.rollout_id}.json")

        if rollout.final_reward is None:
            print(
                f"Warning: Reward is None for rollout {rollout.rollout_id}, will be auto-set to {self.reward_fillna_value}."
            )
        if rollout.triplets is None:
            print(f"Warning: Triplet is None for rollout {rollout.rollout_id}.")
        elif len(rollout.triplets) == 0:
            print(f"Warning: Length of triplets is 0 for rollout {rollout.rollout_id}.")
        elif any(not r.response.get("token_ids", []) for r in rollout.triplets): # TODO: update
            print(f"Warning: Rollout {rollout.rollout_id} contains empty response: {rollout.triplets}")
        elif any(not r.prompt.get("token_ids", []) for r in rollout.triplets):
            print(f"Warning: Rollout {rollout.rollout_id} contains empty prompt: {rollout.triplets}")
    
    def _validate_rollout_for_retry(self, rollout: Rollout) -> bool:                                                                                                                                                                                                       
          """Returns True if rollout should be retried due to empty/invalid data"""                                                                                                                                                                                          
          if not self.enable_rollout_validation:                                                                                                                                                                                                                             
              return False                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                             
          # Check for empty/invalid rollouts                                                                                                                                                                                                                                 
          is_invalid = (                                                                                                                                                                                                                                                     
              rollout.triplets is None or                                                                                                                                                                                                                                    
              len(rollout.triplets) == 0 or
              any(not r.response.get("token_ids", []) for r in rollout.triplets) or
              any(not r.prompt.get("token_ids", []) for r in rollout.triplets)
          )

          if is_invalid:
              data_id = self._get_data_id_from_rollout(rollout)
              retry_count = self._empty_rollout_counts.get(data_id, 0)

              if retry_count < self.max_empty_retries:
                  self._empty_rollout_counts[data_id] = retry_count + 1
                  logger.warning(f"Retrying empty rollout for data_id {data_id} (attempt {retry_count + 1})")
                  return True
              else:
                  logger.error(f"Data_id {data_id} exceeded max empty retries, using fallback")

          return False

    def _get_data_id_from_rollout(self, rollout: Rollout) -> str:
        """Extract data_id from rollout for retry tracking"""
        # Find the original sample data for this rollout
        original_sample = self._task_id_to_original_sample.get(rollout.rollout_id, {})
        return original_sample.get("data_id", rollout.rollout_id)

    async def _async_run_until_finished(self, verbose=True, avg_task_time_sec=150):
        """Async helper to wait for all tasks to complete with dynamic timeout and smart completion"""
        smoke_mode = os.environ.get("AGENTFLOW_SMOKE_MODE", "0") == "1"
        original_task_count = self._total_tasks_queued
        retried_rollout_ids = set()
        start_time = time.time()
        last_progress_time = start_time
        last_completed_count = 0

        # Dynamic timeout: base time per task + buffer for complexity
        estimated_total_time = original_task_count * avg_task_time_sec * 1.5  # 50% buffer
        min_timeout = 120 if smoke_mode else 600   # Smoke: 2 minutes minimum
        max_timeout = 300 if smoke_mode else 3600   # Smoke: 5 minutes maximum
        dynamic_timeout = max(min_timeout, min(max_timeout, estimated_total_time))

        print(f"Starting {original_task_count} {'training' if self.is_train else 'validation'} tasks")
        print(f"Estimated completion time: {dynamic_timeout/60:.1f} minutes (avg {avg_task_time_sec}s per task)")

        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            completed_count = len(self._completed_rollouts)
            completion_rate = completed_count / original_task_count if original_task_count > 0 else 0

            # Check completion conditions
            if completed_count >= self._total_tasks_queued:
                print("All tasks completed")
                break

            # Smart early exit: if >90% done and no progress for 2 minutes
            if completion_rate >= 0.9 and (current_time - last_progress_time) > 120:
                print(f"Early completion: {completion_rate:.1%} tasks done ({completed_count}/{original_task_count})")
                break

            # Dynamic timeout check
            if elapsed > dynamic_timeout:
                print(f"Timeout after {elapsed/60:.1f} minutes. Completed {completion_rate:.1%} ({completed_count}/{original_task_count})")
                break

            # No progress timeout (5 minutes for training, 3 minutes for validation)
            no_progress_limit = 120 if smoke_mode else (300 if self.is_train else 180)
            if (current_time - last_progress_time) > no_progress_limit:
                print(f"No progress for {no_progress_limit/60:.1f} minutes. Completed {completion_rate:.1%}")
                if smoke_mode:
                    print("Smoke mode: accepting current results early.")
                    break
                if not self.is_train or completion_rate >= 0.5:  # Accept if validation or >50% training done
                    print("Accepting current results")
                    break

            try:
                # Prevent indefinite blocking inside server retrieval path.
                retrieve_timeout = 10 if smoke_mode else 60
                completed_batch = await asyncio.wait_for(
                    self.server.retrieve_completed_rollouts(), timeout=retrieve_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(
                    f"Timed out waiting for completed rollouts (>{retrieve_timeout}s); continuing poll loop."
                )
                completed_batch = []

            # Update progress tracking
            if completed_count > last_completed_count:
                last_progress_time = current_time
                last_completed_count = completed_count

            new_retries = 0
            for rollout in completed_batch:
                self._validate_data(rollout)

                # Check if this rollout is from our current session
                if rollout.rollout_id not in self._task_id_to_original_sample:
                    logger.warning(f"Skipping orphaned rollout {rollout.rollout_id} (not from current session)")
                    continue

                # Only retry during training and if this rollout hasn't been retried before
                if (self.is_train and
                    rollout.rollout_id not in retried_rollout_ids and
                    self._validate_rollout_for_retry(rollout)):

                    retry_task_metadata = {"retry": True, "original_rollout_id": rollout.rollout_id}
                    original_sample = self._task_id_to_original_sample[rollout.rollout_id]

                    try:
                        new_rollout_id = await self.server.queue_task(
                            sample=original_sample,
                            mode="train" if self.is_train else "val",
                            resources_id=self._current_resources_id,
                            metadata=retry_task_metadata
                        )
                        self._task_id_to_original_sample[new_rollout_id] = original_sample
                        retried_rollout_ids.add(rollout.rollout_id)
                        self._total_tasks_queued += 1
                        new_retries += 1
                        logger.info(f"Resubmitted rollout {rollout.rollout_id} as {new_rollout_id}")
                    except Exception as e:
                        logger.error(f"Failed to resubmit rollout {rollout.rollout_id}: {e}")
                        # Accept the original rollout even if retry fails
                        self._completed_rollouts[rollout.rollout_id] = rollout
                else:
                    self._completed_rollouts[rollout.rollout_id] = rollout

            if verbose and (elapsed % 30 < 5 or new_retries > 0):  # Log every 30s or when retries happen
                eta_minutes = (dynamic_timeout - elapsed) / 60
                if self.is_train:
                    valid_rollouts = len([r for r in self._completed_rollouts.values()
                                        if r.triplets and len(r.triplets) > 0])
                    print(f"[{elapsed/60:.1f}m] Progress: {completion_rate:.1%} ({completed_count}/{original_task_count}), "
                          f"Valid: {valid_rollouts}, Retries: {new_retries}, ETA: {eta_minutes:.1f}m")
                else:
                    print(f"[{elapsed/60:.1f}m] Validation: {completion_rate:.1%} ({completed_count}/{original_task_count})")

            # Adaptive sleep based on progress
            if len(completed_batch) > 0 or new_retries > 0:
                await asyncio.sleep(2)  # Active progress
            elif completion_rate > 0.8:
                await asyncio.sleep(3)  # Near completion
            else:
                await asyncio.sleep(5)  # Normal waiting

        valid_rollouts = len([r for r in self._completed_rollouts.values()
                            if r.triplets and len(r.triplets) > 0])
        final_elapsed = time.time() - start_time
        final_rate = len(self._completed_rollouts) / original_task_count if original_task_count > 0 else 0

        print(f"Finished after {final_elapsed/60:.1f} minutes. "
              f"Completion rate: {final_rate:.1%} ({len(self._completed_rollouts)}/{original_task_count}), "
              f"Valid rollouts: {valid_rollouts}")

    def run_until_all_finished(self, verbose=True):
        """Synchronously waits for all queued tasks to be completed and reported."""
        if self._total_tasks_queued == 0:
            print("Warning: No tasks were queued.")
            return

        if not self.server.loop or not self.server.startup_event.is_set():
            raise RuntimeError("Server is not running or ready.")

        coro = self._async_run_until_finished(verbose)
        future = asyncio.run_coroutine_threadsafe(coro, self.server.loop)
        try:
            smoke_mode = os.environ.get("AGENTFLOW_SMOKE_MODE", "0") == "1"
            # In smoke mode, enforce a hard daemon-level cap to avoid endless waits.
            daemon_timeout = 600 if smoke_mode else None  # Smoke: 10 minutes max
            future.result(timeout=daemon_timeout)
        except TimeoutError:
            logger.error(
                "AgentModeDaemon run_until_all_finished timed out in smoke mode; "
                "aborting step early."
            )
            raise RuntimeError("Smoke-mode daemon timeout while waiting for rollouts.")
        except Exception as e:
            print(f"Error while waiting for tasks to finish: {e}")
            raise

    def get_test_metrics(self):
        """Calculates and returns metrics for a validation run."""
        assert not self.is_train, "This method should only be called during validation."

        # With retry logic, we might have more/less completed rollouts than originally queued
        # Log the actual counts for debugging
        logger.info(f"Validation completed: {len(self._completed_rollouts)} rollouts out of {self._total_tasks_queued} total tasks")

        if len(self._completed_rollouts) == 0:
            logger.warning("No completed rollouts found for validation metrics calculation")
            return {
                "val/reward": 0.0,
                "val/mean_response_length": 0.0,
                "val/sum_response_length": 0.0,
                "val/turn_count": 0.0,
            }

        sample_stat_list = []
        for rollout_id, rollout in self._completed_rollouts.items():
            if not rollout.triplets:
                continue
            response_length_list = [len(triplet.response.get("token_ids", [])) for triplet in rollout.triplets]
            final_reward = self._fillna_reward(rollout)
            sample_stat_list.append(
                {
                    "sum_response_length": np.sum(response_length_list),
                    "mean_response_length": np.mean(response_length_list) if response_length_list else 0,
                    "turn_count": len(rollout.triplets),
                    "reward": final_reward,
                }
            )

        return {
            "val/reward": np.mean([stat["reward"] for stat in sample_stat_list]),
            "val/mean_response_length": np.mean([stat["mean_response_length"] for stat in sample_stat_list]),
            "val/sum_response_length": np.mean([stat["sum_response_length"] for stat in sample_stat_list]),
            "val/turn_count": np.mean([stat["turn_count"] for stat in sample_stat_list]),
        }

    def get_train_data_batch(self, max_prompt_length, max_response_length, device):
        """
        Processes completed rollouts to generate a training data batch.

        This function reconstructs the logic from the original AgentModeDaemon,
        using data retrieved from the new server architecture. It handles padding,
        truncation, and tensor creation for the PPO training loop.
        """
        assert self.is_train, "This method should only be called during training."

        # With retry logic, we might have more/less completed rollouts than originally queued
        # Log the actual counts for debugging
        logger.info(f"Training completed: {len(self._completed_rollouts)} rollouts out of {self._total_tasks_queued} total tasks")

        # 1. Reconstruct the `finished_id_to_sample_info` structure from completed rollouts
        finished_id_to_sample_info = {}
        skipped_rollouts = 0

        for rollout_id, rollout in self._completed_rollouts.items():
            # Skip orphaned rollouts that don't have original sample data
            if rollout_id not in self._task_id_to_original_sample:
                logger.warning(f"Skipping orphaned rollout {rollout_id} in training batch creation")
                skipped_rollouts += 1
                continue

            original_sample = self._task_id_to_original_sample[rollout_id]

            if not rollout.triplets:
                continue

            # The client should report triplets that contain prompt_ids and response_ids.
            # Example triplet.prompt: {"token_ids": [...]}
            # Example triplet.response: {"token_ids": [...]}
            trace_list = [
                {
                    "prompt_ids": self._extract_token_ids(getattr(t, "prompt", None)),
                    "response_ids": self._extract_token_ids(getattr(t, "response", None)),
                }
                for t in rollout.triplets
            ]
            if not any(len(x["prompt_ids"]) + len(x["response_ids"]) > 0 for x in trace_list):
                question_text = str(original_sample.get("question", "")).strip()
                rollout_text = self._extract_rollout_text(rollout)
                prompt_ids = []
                response_ids = []
                if question_text:
                    try:
                        prompt_ids = self.tokenizer.encode(question_text, add_special_tokens=False)
                    except Exception:
                        prompt_ids = []
                if rollout_text:
                    try:
                        response_ids = self.tokenizer.encode(rollout_text, add_special_tokens=False)
                    except Exception:
                        response_ids = []
                if not response_ids:
                    response_ids = [self.pad_token_id]
                    payload = getattr(rollout, "__dict__", {})
                    available_keys = list(payload.keys()) if isinstance(payload, dict) else []
                    logger.warning(
                        f"Fallback response text missing for rollout {rollout_id}; "
                        f"using pad-token response. rollout_keys={available_keys}"
                    )
                trace_list = [{"prompt_ids": prompt_ids, "response_ids": response_ids}]
                logger.warning(
                    f"Synthesized fallback trace for rollout {rollout_id} "
                    f"(prompt_tokens={len(prompt_ids)}, response_tokens={len(response_ids)})."
                )

            final_reward = self._fillna_reward(rollout)
            info = {
                "reward": final_reward,
                "trace_list": trace_list,
                "data_id": original_sample["data_id"],
            }
            finished_id_to_sample_info[rollout_id] = info

        # Log rollout processing summary
        if skipped_rollouts > 0:
            logger.warning(f"Skipped {skipped_rollouts} orphaned rollouts during training batch creation")

        # data no empty check
        if not finished_id_to_sample_info:
            raise ValueError(f"No valid rollout data found. Cannot create training batch. "
                           f"Total rollouts: {len(self._completed_rollouts)}, Skipped: {skipped_rollouts}")
        #
        # --- Data processing and tensor creation logic ---
        # Get all the reported data.
        # prompt_ids are left-padded.
        # response_ids are right-padded.
        # They are concatenated in the middle.
        # Discard handling:
        #   - Those exceeding max_prompt_length will be marked for discard, but not
        #     discarded here. They are only truncated and marked, to be discarded later.
        #     This is for the correctness of the advantage calculation.
        #   - The discard for the PPO mini-batch should also be handled this way.
        input_ids_list, input_attention_mask_list = [], []
        response_ids_list, response_attention_mask_list = [], []
        reward_list, data_id_list, rollout_id_list, turn_index_list, is_drop_list = [], [], [], [], []
        n_trunc_sample_because_of_response = 0
        valid_samples = 0
        all_samples_num = 0
        for rollout_id, sample_info in finished_id_to_sample_info.items():
            for turn_index, trace in enumerate(sample_info["trace_list"]):

                reward_list.append(sample_info["reward"])
                prompt_ids, response_ids = trace["prompt_ids"], trace["response_ids"]
                all_samples_num += 1
                
                if len(prompt_ids) == 0 and len(response_ids) == 0:
                    reward_list = reward_list[:-1]
                    continue
                else:
                    valid_samples += 1

                # Mark samples with prompts exceeding max_prompt_length to be dropped later
                if len(prompt_ids) > max_prompt_length:
                    prompt_ids = prompt_ids[:max_prompt_length]
                    is_drop_list.append(True)
                else:
                    is_drop_list.append(False)

                # Truncate responses that exceed max_response_length
                if len(response_ids) > max_response_length:
                    response_ids = response_ids[:max_response_length]
                    n_trunc_sample_because_of_response += 1

                # Pad prompts to the left and responses to the right
                one_input_ids, one_input_attention_mask = get_left_padded_ids_and_attention_mask(
                    prompt_ids, max_prompt_length, self.pad_token_id
                )
                one_response_ids, one_response_attention_mask = get_right_padded_ids_and_attention_mask(
                    response_ids, max_response_length, self.pad_token_id
                )

                input_ids_list.append(one_input_ids)
                input_attention_mask_list.append(one_input_attention_mask)
                response_ids_list.append(one_response_ids)
                response_attention_mask_list.append(one_response_attention_mask)
                data_id_list.append(sample_info["data_id"])
                rollout_id_list.append(rollout_id)
                turn_index_list.append(turn_index)

        print(f"[STEP-WISE DEBUG]: valid response trace length in this training step is [{valid_samples}/{all_samples_num}]")
        if valid_samples == 0:
            raise RuntimeError(
                "No valid response traces available for training batch creation. "
                f"valid_samples={valid_samples}, all_samples={all_samples_num}, "
                f"completed_rollouts={len(self._completed_rollouts)}, total_queued={self._total_tasks_queued}. "
                "This usually means rollouts completed but produced empty prompt/response token_ids."
            )

        # CHECK
        if not input_ids_list:
            raise ValueError("No valid input data found. All rollouts might be empty.")

        n_transition = len(input_ids_list)
        # CHECK
        if n_transition == 0:
            raise ValueError("No transitions to process. Cannot create training batch.")

        n_transition = len(input_ids_list)
        batch_input_ids = torch.LongTensor(input_ids_list).to(device)
        input_attention_mask = torch.LongTensor(input_attention_mask_list).to(device)
        batch_response_ids = torch.LongTensor(response_ids_list).to(device)
        response_attention_mask = torch.LongTensor(response_attention_mask_list).to(device)

        # Concatenate prompts and responses to form the full sequence
        batch_seq = torch.cat([batch_input_ids, batch_response_ids], dim=-1)
        attention_mask = torch.cat([input_attention_mask, response_attention_mask], dim=-1)
        position_ids = torch.clamp(torch.cumsum(attention_mask, dim=-1) - 1, min=0)
        is_drop_mask = torch.BoolTensor(is_drop_list).to(device)
        scores = torch.tensor(reward_list, dtype=torch.bfloat16).to(device)

        # Create token-level scores by placing the final reward at the last token position
        token_level_scores = torch.zeros_like(attention_mask, dtype=scores.dtype)
        # At the eos_mask_idx position of each sample, fill in the corresponding scores.
        # torch.arange(n_transition) generates [0,1,2,...,bsz-1] as indices for the batch dimension.
        eos_mask_idx = torch.argmax(position_ids * attention_mask, dim=-1)  # (bsz,)
        token_level_scores[torch.arange(n_transition), eos_mask_idx] = scores
        # Only take the last response_length part of the sequence to get the token-level scores for the model's response part.
        token_level_scores = token_level_scores[:, -max_response_length:]

        # Form the final batch using TensorDict
        batch = TensorDict(
            {
                "prompts": batch_input_ids,
                "responses": batch_response_ids,
                "input_ids": batch_seq,  # here input_ids become the whole sentences
                "attention_mask": attention_mask,
                "position_ids": position_ids,
                "is_drop_mask": is_drop_mask,
                "token_level_scores": token_level_scores.contiguous(),
            },
            batch_size=n_transition,
        )
        data_proto = DataProto(batch=batch)

        data_metrics = {
            "agent_mode/n_trunc_sample_because_of_response": n_trunc_sample_because_of_response,
            "agent_mode/n_sample_to_train": n_transition,
        }

        # Add non-tensor data for advantage calculation and logging
        data_proto.non_tensor_batch["data_id_list"] = np.array(data_id_list)
        data_proto.non_tensor_batch["rollout_id_list"] = np.array(rollout_id_list)
        data_proto.non_tensor_batch["turn_index_list"] = np.array(turn_index_list)

        return data_proto, data_metrics

    def clear_data_and_server(self):
        """Resets the internal state of the daemon for the next run."""
        self.backend_llm_server_addresses = []
        self._completed_rollouts.clear()
        self._task_id_to_original_sample.clear()
        self._total_tasks_queued = 0
        self._empty_rollout_counts.clear()  # Clear retry counters
        self._current_resources_id = None

        # For a true reset, the server's internal queues would also need clearing.
        # This implementation assumes that `set_up_data_and_server` is called
        # for each new run, effectively starting a fresh batch.
        # extra status clearup
        self.is_train = True
        # server rollout clearup
        if hasattr(self.server, 'clear_queues'):
            self.server.clear_queues()

    def _fillna_reward(self, rollout):
        if rollout.final_reward is None:
            if self.reward_fillna_value is not None:
                final_reward = self.reward_fillna_value
            else:
                raise ValueError(f"Reward is None for rollout {rollout.rollout_id}, please check the reward function.")
        else:
            final_reward = rollout.final_reward
        return final_reward

    def _extract_token_ids(self, obj) -> list[int]:
        """
        Robustly extract token ids from rollout prompt/response payloads.

        Some backends may not populate `token_ids` but provide equivalent fields
        (e.g. `ids`, `input_ids`) or plain text content only.
        """
        if obj is None:
            return []

        # Fast path: dict-like with token/id arrays.
        if isinstance(obj, dict):
            for key in ("token_ids", "input_ids", "ids"):
                value = obj.get(key)
                if isinstance(value, list) and len(value) > 0:
                    try:
                        return [int(x) for x in value]
                    except Exception:
                        pass

            # Fallback: tokenize text if ids are missing.
            for key in ("text", "content", "message", "value"):
                value = obj.get(key)
                if isinstance(value, str) and value.strip():
                    try:
                        return self.tokenizer.encode(value, add_special_tokens=False)
                    except Exception:
                        return []
            return []

        # Object-like payloads with attributes.
        for key in ("token_ids", "input_ids", "ids"):
            value = getattr(obj, key, None)
            if isinstance(value, list) and len(value) > 0:
                try:
                    return [int(x) for x in value]
                except Exception:
                    pass

        for key in ("text", "content", "message", "value"):
            value = getattr(obj, key, None)
            if isinstance(value, str) and value.strip():
                try:
                    return self.tokenizer.encode(value, add_special_tokens=False)
                except Exception:
                    return []

        return []

    def _extract_rollout_text(self, rollout) -> str:
        """Best-effort extraction of rollout text payload."""
        for key in ("final_output", "output", "response", "result", "text", "content"):
            value = getattr(rollout, key, None)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                for k2 in ("text", "content", "final_output", "response"):
                    v2 = value.get(k2)
                    if isinstance(v2, str) and v2.strip():
                        return v2.strip()

        payload = getattr(rollout, "__dict__", None)
        if isinstance(payload, dict):
            for key in ("final_output", "output", "response", "result", "text", "content"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
                if isinstance(value, dict):
                    for k2 in ("text", "content", "final_output", "response"):
                        v2 = value.get(k2)
                        if isinstance(v2, str) and v2.strip():
                            return v2.strip()
        return ""
