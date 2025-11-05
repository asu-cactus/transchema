import json

def _json_safe(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)

def _extract_hit(hit, output_fields):
    item = {}
    # id / pk
    for k in ("id", "pk", "primary_key"):
        v = getattr(hit, k, None)
        if v is None:
            try:
                v = hit.get(k)  # some SDKs make Hit mapping-like
            except Exception:
                pass
        if v is not None:
            item["id"] = _json_safe(v)
            break

    # distance / score
    for k in ("distance", "score"):
        v = getattr(hit, k, None)
        if v is None:
            try:
                v = hit.get(k)
            except Exception:
                pass
        if v is not None:
            try:
                item[k] = float(v)
            except Exception:
                item[k] = _json_safe(v)

    # payload fields (entity/fields vary by SDK)
    ent = getattr(hit, "entity", None)
    for f in output_fields:
        v = None
        if hasattr(hit, f):
            v = getattr(hit, f)
        if v is None:
            try:
                v = hit.get(f)
            except Exception:
                pass
        if v is None and ent is not None:
            try:
                v = ent.get(f)
            except Exception:
                v = getattr(ent, f, None)
        if v is not None:
            item[f] = _json_safe(v)

    # fallback: if item is still empty, stringify the hit
    if not item:
        item = {"raw": str(hit)}
    return item

def milvus_results_to_json(results, output_fields):
    """
    Normalize Milvus search results into a list[dict] that is JSON-serializable.
    Works across common pymilvus client shapes.
    """
    # Some clients return {"data": [...]}
    if isinstance(results, dict) and "data" in results:
        results = results["data"]

    hits = []
    if isinstance(results, list):
        # Often shape is list[list[Hit]] (one list per query)
        # If so, flatten the first query's hits for now
        inner = results[0] if results and isinstance(results[0], list) else results
        for h in inner:
            hits.append(_extract_hit(h, output_fields))
    else:
        hits.append(_extract_hit(results, output_fields))

    return hits
