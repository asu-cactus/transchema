import sys
sys.path.insert(0, ".")
from analyze_run8_early_stopping_all_methods import process_case, METHOD_NAMES

for c in [18, 72, 92, 94]:
    case_num, out = process_case(c)
    print(f"\nc{c}:")
    if out is None:
        print("  NO LOG / 0 iters")
        continue
    for name in METHOD_NAMES:
        score, ok = out[name]
        score_s = f"{score:.4f}" if score is not None else "N/A"
        print(f"  {name:<18} score={score_s:<10} {'OK' if ok else 'WRONG'}")
