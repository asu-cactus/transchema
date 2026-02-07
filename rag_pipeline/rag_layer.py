from pymilvus import MilvusClient
from tqdm.auto import tqdm
from .milvus_result_utils import milvus_results_to_json
import torch
import numpy as np
import torch.nn.functional as F
from torch import Tensor
import os, json
from typing import Dict, Optional, List, Any
from transformers import AutoTokenizer, AutoModel


# Keep tokenizer/model threading tame (helps on macOS)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

def last_token_pool(last_hidden_states,
                 attention_mask, device):
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    else:
        sequence_lengths = attention_mask.sum(dim=1) - 1
        batch_size = last_hidden_states.shape[0]
        return last_hidden_states[torch.arange(batch_size, device=device), sequence_lengths]


class EmbeddingLayer:
    def __init__(
        self, 
        embedding_model="Qwen/Qwen3-Embedding-8B", 
        max_seq_length=512,
        device="auto"
    ):
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self.device = device
        print(f"[INFO] Using device: {self.device}")
        self.max_seq_len = max_seq_length
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model, padding_side='left', trust_remote_code=True)
        self.model = AutoModel.from_pretrained(embedding_model, trust_remote_code=True).to(self.device).eval()

    
    def encode(self, docs, is_query=False, normalize_embeddings=True, batch_size=1):
        encoded_docs = []
        pbar = tqdm(range(0, len(docs), batch_size), desc="Encoding Documents")

        with torch.inference_mode():
            for start in pbar:
                batch = docs[start : start + batch_size]
                embeddings = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=self.max_seq_len,
                    return_tensors='pt'
                )
                embeddings = {k: v.to(self.device) for k, v in embeddings.items()}
                out = self.model(**embeddings)

                if getattr(out, "pooler_output", None) != None:
                    new_out = out.pooler_output
                elif hasattr(out, "last_hidden_state"):
                    new_out = last_token_pool(out.last_hidden_state, embeddings["attention_mask"], self.device)
                
                if normalize_embeddings:
                    new_out = F.normalize(new_out, p=2, dim=-1)
                
                encoded_docs.append(new_out.detach().cpu())
                print(new_out.shape)
        return encoded_docs


class RAGDB:
    def __init__(self, uri="milvus.db", collection="rag_min",
                 model_id="Qwen/Qwen3-Embedding-0.6B", max_len=8192, device="auto"):
        self.uri = uri
        self.client = MilvusClient(uri)
        self.collection = collection
        self.embedder = EmbeddingLayer(embedding_model=model_id, max_seq_length=max_len, device=device)

        # infer dim
        dim = self._embed(["__probe__"], bs=1).shape[1]

        # make collection (once), add index, load
        if not self.client.has_collection(collection):
            self.client.create_collection(collection_name=collection, dimension=dim,
                                          metric_type="COSINE", 
                                          auto_id=True, enable_dynamic_field=True)
        try:
            self.client.load_collection(collection)
        except Exception:
            pass

    def insert_texts(self, texts, case_ids=None):
        """
        Insert texts into the database.
        
        Args:
            texts: List of text strings to insert
            case_ids: Optional list of case_id strings (e.g., ["4_24", "4_32"])
                      If provided, must be same length as texts
        """
        vecs = self._embed(texts)

        rows = [
            {
                "doc": texts[i], 
                "vector": vecs[i].tolist(),
                "case_id": case_ids[i] if case_ids and i < len(case_ids) else None,
            } 
            for i in range(len(texts))
        ]
        self.client.insert(collection_name=self.collection, data=rows)
        return True

    def search(self, queries, top_k=5, batch_size=32, output_fields=None, exclude_case_id: Optional[str] = None):
        """
        Search for similar documents using vector similarity.

        Args:
            queries: List of query strings
            top_k: Number of results to return
            batch_size: Batch size for embedding
            output_fields: Optional list of fields to return. Defaults to ["id", "doc", "case_id"]
            exclude_case_id: Optional case_id to exclude (e.g., "4_52" for self-retrieval prevention).
                Uses Milvus filter when supported; caller should still post-filter as fallback.
                When set, requests top_k + 5 results to compensate for filtered/excluded hits.
        """
        qvecs = self._embed(queries, bs=batch_size)

        if output_fields is None:
            output_fields = ["id", "doc", "case_id"]

        # When excluding same-case, request extra results to compensate (caller will post-filter)
        limit = top_k + 5 if exclude_case_id else top_k

        # Smart fallback: try Milvus filter first, fall back to unfiltered search if it fails
        filter_expr = ""
        if exclude_case_id:
            # Escape quotes in case_id if needed
            safe_id = str(exclude_case_id).replace('"', '\\"')
            filter_expr = f'case_id != "{safe_id}"'

        try:
            if filter_expr:
                return self.client.search(
                    collection_name=self.collection,
                    data=qvecs.tolist(),
                    filter=filter_expr,
                    limit=limit,
                    output_fields=output_fields,
                    search_params={"params": {"ef": 64}}
                )
            else:
                return self.client.search(
                    collection_name=self.collection,
                    data=qvecs.tolist(),
                    limit=limit,
                    output_fields=output_fields,
                    search_params={"params": {"ef": 64}}
                )
        except Exception:
            # Fallback: Milvus filter not supported (e.g., case_id not filterable) - search without filter
            return self.client.search(
                collection_name=self.collection,
                data=qvecs.tolist(),
                limit=limit,
                output_fields=output_fields,
                search_params={"params": {"ef": 64}}
            )

    # ----- tiny helper -----
    def _embed(self, texts, bs=32):
        chunks = self.embedder.encode(list(texts), batch_size=bs, normalize_embeddings=True)
        if isinstance(chunks, list):
            with torch.no_grad():
                x = torch.cat(chunks, dim=0).to(torch.float32).cpu().numpy()
        else:
            x = chunks.to(torch.float32).cpu().numpy()
        return x


if __name__ == "__main__":
    db = RAGDB(
        uri="rag_pipeline/db/milvus_demo_4.db",
        collection="plan_docs",
        model_id="Qwen/Qwen3-Embedding-0.6B",
        device="auto",
    )

    # Search
    queries = [
        "debt consolidation",
    ]
    results = db.search(queries, top_k=2)

    print("\n--- Normalized hits (first query) ---")
    norm = milvus_results_to_json(results, output_fields=["doc"])
    print(json.dumps(norm, indent=2))
