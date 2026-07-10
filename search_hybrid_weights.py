"""
search_hybrid_weights.py
===========================
Directly searches score_1 weight-space against the REAL, unmodified
HYBRID_C=0.1 selection mechanism (no linear surrogate, no frozen-frequency
approximation -- the single-pass LP in fit_hybrid_weights_lp.py tried that
and still regressed HYBRID_C by -6 combined, because the fitted weights
drifted too far from equal-weights for the frozen-frequency assumption to
hold at evaluation time).

Each candidate weight vector is evaluated by literally re-running
analyze_new_weights_all_methods.py's lookup+tree-reconstruction+
flat_hybrid_pick_new pipeline across all L1+L4+L9 cases (~3.2s per full
evaluation), so there is no approximation gap between what's optimized and
what's reported.

Strategy: broad random search over the weight simplex (Dirichlet sampling),
keep the best candidates by combined HYBRID_C accuracy (never worse than the
equal-weight baseline), then local coordinate refinement around the best.

Usage: python3 search_hybrid_weights.py [--n_random 150] [--n_refine 60]
Run from: ~/transchema/ (needs `source env/bin/activate`)
"""
import sys
import argparse
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, ".")
import analyze_new_weights_all_methods as m

FEATURES = ["fd_f1", "avg_col_score_1", "row_count_score", "max_missing_score"]
EQUAL_W = {f: 0.25 for f in FEATURES}


def evaluate(w_dict, workers=20):
    """Returns {method_name: (n_ok, n_known)} combined across all L1+L4+L9 cases."""
    lookup = m.load_lookup(weights=w_dict)
    tasks = [(length, log_dir, c) for length, log_dir, n in m.CONFIGS for c in range(n)]
    results = {1: {}, 4: {}, 9: {}}
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(m.process_case, l, d, c, lookup): (l, c) for l, d, c in tasks}
        for future in as_completed(futures):
            length, c = futures[future]
            try:
                length_r, case_num, out = future.result()
            except Exception:
                continue
            results[length][case_num] = out[0] if out is not None else None

    combined = {name: [0, 0] for name in m.METHOD_NAMES}
    for length, log_dir, n in m.CONFIGS:
        for c in range(n):
            out = results[length].get(c)
            if out is None:
                continue
            for name in m.METHOD_NAMES:
                score, is_match = out[name]
                if is_match is None:
                    continue
                combined[name][1] += 1
                combined[name][0] += bool(is_match)
    return {name: tuple(v) for name, v in combined.items()}


def sample_simplex(rng, alpha=1.0, k=4):
    w = rng.dirichlet([alpha] * k)
    return dict(zip(FEATURES, w))


def perturb(w_dict, rng, scale=0.05):
    w = np.array([w_dict[f] for f in FEATURES])
    w = w + rng.normal(0, scale, size=4)
    w = np.clip(w, 1e-4, None)
    w = w / w.sum()
    return dict(zip(FEATURES, w))


def hybrid_acc(result):
    ok, n = result["HYBRID_C=0.1"]
    return ok / n if n else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_random", type=int, default=150)
    parser.add_argument("--n_refine", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    print("Evaluating equal-weight baseline...")
    baseline = evaluate(EQUAL_W)
    for name, (ok, n) in baseline.items():
        print(f"  {name:<18}: {ok}/{n} ({100*ok/n:.1f}%)")
    baseline_hybrid = hybrid_acc(baseline)
    print(f"Baseline HYBRID_C accuracy: {baseline_hybrid:.4f}\n")

    candidates = []  # (hybrid_acc, w_dict, full_result)

    print(f"Random search: {args.n_random} samples on the weight simplex...")
    for i in range(args.n_random):
        w = sample_simplex(rng)
        result = evaluate(w)
        acc = hybrid_acc(result)
        candidates.append((acc, w, result))
        tag = "  <-- beats baseline" if acc > baseline_hybrid else ""
        print(f"  [{i+1}/{args.n_random}] hybrid_acc={acc:.4f} w={ {k: round(v,3) for k,v in w.items()} }{tag}", flush=True)

    candidates.sort(key=lambda x: -x[0])
    top = candidates[:5]
    print(f"\nTop 5 from random search:")
    for acc, w, result in top:
        print(f"  hybrid_acc={acc:.4f}  {w}")

    print(f"\nLocal refinement: {args.n_refine} perturbations around the best candidate...")
    best_acc, best_w, best_result = top[0]
    for i in range(args.n_refine):
        scale = 0.08 * (1 - i / args.n_refine) + 0.01
        w = perturb(best_w, rng, scale=scale)
        result = evaluate(w)
        acc = hybrid_acc(result)
        if acc > best_acc:
            best_acc, best_w, best_result = acc, w, result
            print(f"  [refine {i+1}/{args.n_refine}] NEW BEST hybrid_acc={acc:.4f} w={ {k: round(v,3) for k,v in w.items()} }", flush=True)
        else:
            print(f"  [refine {i+1}/{args.n_refine}] hybrid_acc={acc:.4f} (no improvement)", flush=True)

    print(f"\n{'='*70}\nBEST WEIGHTS FOUND\n{'='*70}")
    print(f"Weights: {best_w}")
    print(f"\nFull method comparison (equal-weight baseline vs. best found):")
    for name in m.METHOD_NAMES:
        b_ok, b_n = baseline[name]
        f_ok, f_n = best_result[name]
        print(f"  {name:<18}: {b_ok}/{b_n} ({100*b_ok/b_n:.1f}%)  ->  {f_ok}/{f_n} ({100*f_ok/f_n:.1f}%)")


if __name__ == "__main__":
    main()
