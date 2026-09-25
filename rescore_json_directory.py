#!/usr/bin/env python3
"""
Create a rescored copy of experiment JSON logs using a CSV score table.

For each (case, iteration, source), the new score is:
    (fd_f1 + js_sim + col_ratio) / 3

The script reads JSON files from an input directory and writes updated files to
an output directory, leaving the input directory untouched.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ScoreKey = tuple[str, int, str]
ScoreValue = float | None


def _parse_optional_float(raw_value: str | None, field: str, row_number: int) -> float | None:
    if raw_value is None or raw_value == "":
        return None
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"CSV row {row_number}: could not parse '{field}' as float: {raw_value!r}"
        ) from exc


def load_score_map(
    csv_path: Path,
    round_digits: int | None,
    missing_policy: str,
    score_columns: tuple[str, str, str],
) -> tuple[dict[ScoreKey, ScoreValue], int]:
    required_columns = {"case", "iteration", "source", *score_columns}
    score_map: dict[ScoreKey, ScoreValue] = {}
    missing_metric_rows = 0

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = required_columns - fieldnames
        if missing_columns:
            missing_str = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required columns: {missing_str}")

        for row_number, row in enumerate(reader, start=2):
            case = (row.get("case") or "").strip()
            if not case:
                raise ValueError(f"CSV row {row_number}: missing case value.")

            iteration_raw = (row.get("iteration") or "").strip()
            if not iteration_raw:
                raise ValueError(f"CSV row {row_number}: missing iteration value.")
            try:
                iteration = int(iteration_raw)
            except ValueError as exc:
                raise ValueError(
                    f"CSV row {row_number}: invalid iteration {iteration_raw!r}."
                ) from exc

            source = (row.get("source") or "").strip() or "ms"

            metric_values = [
                _parse_optional_float(row.get(column), column, row_number)
                for column in score_columns
            ]

            key = (case, iteration, source)
            if key in score_map:
                raise ValueError(f"Duplicate CSV key found: {key}")
            if any(value is None for value in metric_values):
                missing_metric_rows += 1
                if missing_policy == "error":
                    raise ValueError(
                        "CSV row "
                        f"{row_number} has missing metrics for key {key}. "
                        "Use --missing-policy keep_old or --missing-policy zero to continue."
                    )
                if missing_policy == "keep_old":
                    score_map[key] = None
                    continue
                if missing_policy == "zero":
                    metric_values = [
                        0.0 if value is None else value for value in metric_values
                    ]
                else:
                    raise ValueError(f"Unsupported missing policy: {missing_policy}")

            assert all(value is not None for value in metric_values)
            new_score = sum(metric_values) / 3.0
            if round_digits is not None:
                new_score = round(new_score, round_digits)
            score_map[key] = new_score

    return score_map, missing_metric_rows


def _normalize_iteration(iteration_value: object, file_name: str) -> int:
    if isinstance(iteration_value, int):
        return iteration_value
    if isinstance(iteration_value, str) and iteration_value.isdigit():
        return int(iteration_value)
    raise ValueError(f"{file_name}: invalid iteration value {iteration_value!r}")


def update_scores_in_json(
    payload: dict, score_map: dict[ScoreKey, ScoreValue], file_name: str
) -> tuple[int, int, list[ScoreKey], set[ScoreKey]]:
    case = payload.get("case")
    if not isinstance(case, str) or not case:
        raise ValueError(f"{file_name}: missing or invalid 'case'.")

    iterations = payload.get("iterations")
    if not isinstance(iterations, list):
        raise ValueError(f"{file_name}: missing or invalid 'iterations'.")

    replaced = 0
    kept_old = 0
    missing: list[ScoreKey] = []
    used_keys: set[ScoreKey] = set()

    for item in iterations:
        if not isinstance(item, dict):
            continue
        iteration = _normalize_iteration(item.get("iteration"), file_name)

        ms_entry = item.get("ms")
        if isinstance(ms_entry, dict) and "score" in ms_entry:
            key = (case, iteration, "ms")
            if key not in score_map:
                missing.append(key)
            else:
                used_keys.add(key)
                new_score = score_map[key]
                if new_score is None:
                    kept_old += 1
                else:
                    ms_entry["score"] = new_score
                    replaced += 1

        critiques = item.get("critiques", [])
        if isinstance(critiques, list):
            for idx, critique in enumerate(critiques):
                if not isinstance(critique, dict) or "score" not in critique:
                    continue
                source = critique.get("type") or f"critique_{idx}"
                if not isinstance(source, str):
                    source = str(source)
                key = (case, iteration, source)
                if key not in score_map:
                    missing.append(key)
                else:
                    used_keys.add(key)
                    new_score = score_map[key]
                    if new_score is None:
                        kept_old += 1
                    else:
                        critique["score"] = new_score
                        replaced += 1

    return replaced, kept_old, missing, used_keys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy and rescore a directory of JSON experiment logs."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing original JSON log files.",
    )
    parser.add_argument(
        "--csv-path",
        required=True,
        help="CSV with columns case, iteration, source, fd_f1, js_sim, col_ratio.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where rescored JSON files will be written.",
    )
    parser.add_argument(
        "--round-digits",
        type=int,
        default=None,
        help="Optional number of decimals to round new scores to.",
    )
    parser.add_argument(
        "--missing-policy",
        choices=["error", "keep_old", "zero"],
        default="keep_old",
        help=(
            "How to handle rows where fd_f1/js_sim/col_ratio are missing: "
            "'error' stops, 'keep_old' leaves JSON score unchanged, 'zero' "
            "treats missing metrics as 0."
        ),
    )
    parser.add_argument(
        "--score-columns",
        nargs=3,
        default=["fd_f1", "js_sim", "col_ratio"],
        metavar=("COL1", "COL2", "COL3"),
        help=(
            "Three CSV columns used in the score average. "
            "Default: fd_f1 js_sim col_ratio."
        ),
    )
    parser.add_argument(
        "--json-indent",
        type=int,
        default=2,
        help="Indent to use when writing output JSON files (default: 2).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    csv_path = Path(args.csv_path).resolve()

    if not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")
    if not csv_path.is_file():
        raise SystemExit(f"CSV file does not exist: {csv_path}")

    if output_dir.exists():
        if not output_dir.is_dir():
            raise SystemExit(f"Output path exists and is not a directory: {output_dir}")
        if any(output_dir.iterdir()):
            raise SystemExit(
                f"Output directory is not empty: {output_dir}\n"
                "Please provide an empty directory path."
            )
    else:
        output_dir.mkdir(parents=True, exist_ok=False)

    score_map, missing_metric_rows = load_score_map(
        csv_path,
        args.round_digits,
        args.missing_policy,
        tuple(args.score_columns),
    )

    input_files = sorted(path for path in input_dir.iterdir() if path.is_file())
    if not input_files:
        raise SystemExit(f"No files found in input directory: {input_dir}")

    total_replaced = 0
    total_kept_old = 0
    all_missing: list[tuple[str, ScoreKey]] = []
    used_keys: set[ScoreKey] = set()

    for input_path in input_files:
        with input_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        replaced, kept_old, missing, used_in_file = update_scores_in_json(
            data, score_map, input_path.name
        )
        total_replaced += replaced
        total_kept_old += kept_old
        used_keys.update(used_in_file)
        for key in missing:
            all_missing.append((input_path.name, key))

        output_path = output_dir / input_path.name
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=args.json_indent, ensure_ascii=True)
            handle.write("\n")

    if all_missing:
        sample = "\n".join(
            f"  {file_name}: {key}" for file_name, key in all_missing[:15]
        )
        raise SystemExit(
            f"Missing CSV rows for {len(all_missing)} JSON score entries.\n"
            f"Examples:\n{sample}"
        )

    unused_csv_keys = set(score_map) - used_keys

    print(f"Input directory : {input_dir}")
    print(f"CSV path        : {csv_path}")
    print(f"Score columns   : {tuple(args.score_columns)}")
    print(f"Output directory: {output_dir}")
    print(f"Files processed : {len(input_files)}")
    print(f"Scores replaced : {total_replaced}")
    print(f"Scores kept old : {total_kept_old}")
    print(f"CSV rows read   : {len(score_map)}")
    print(f"Rows w/ missing : {missing_metric_rows}")
    print(f"Unused CSV rows : {len(unused_csv_keys)}")


if __name__ == "__main__":
    main()
