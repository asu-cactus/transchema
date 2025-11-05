from pymilvus import MilvusClient
from tqdm.auto import tqdm
from .milvus_result_utils import milvus_results_to_json
import torch
import numpy as np
import torch.nn.functional as F
from torch import Tensor
import uuid, os, json
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
            # self.client.create_index(collection_name=collection,
            #                          index_params={"index_type": "HNSW", "metric_type": "COSINE",
            #                                        "params": {"M": 16, "efConstruction": 200}})
        try:
            self.client.load_collection(collection)
        except Exception:
            pass

    def insert_texts(self, texts):
        vecs = self._embed(texts)
        # ids = [str(uuid.uuid4()) for _ in texts]
        rows = [{"doc": texts[i], "vector": vecs[i].tolist()} for i in range(len(texts))]
        self.client.insert(collection_name=self.collection, data=rows)
        return True

    def search(self, queries, top_k=5, batch_size=32):
        qvecs = self._embed(queries, bs=batch_size)
        return self.client.search(collection_name=self.collection,
                                  data=qvecs.tolist(),
                                  limit=top_k,
                                  output_fields=["id", "doc"],
                                  search_params={"params": {"ef": 64}})

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
    # try:
    #     os.remove("rag_pipeline/test_dummy/milvus_demo_0.db")
    # except:
    #     pass


    db = RAGDB(
        uri="rag_pipeline/test_dummy/milvus_demo_4.db",
        collection="plan_docs",
        model_id="Qwen/Qwen3-Embedding-0.6B",
        # max_len=8192,
        device="auto",
    )

    # 2) Insert docs
    # docs = [
    #     "Beijing is the capital of China.",
    #     "Phoenix is the capital of Arizona.",
    #     "Gravity is a force that attracts two bodies toward each other.",
    #     "Tucson is a city in Arizona.",
    # ]
    # ok = db.insert_texts(docs)
    # print(f"Inserted {len(docs)} docs: {ok}")

    # Search
    queries = [
        "debt consolidation",
    ]
    results = db.search(queries, top_k=2)

    print("\n--- Normalized hits (first query) ---")
    norm = milvus_results_to_json(results, output_fields=["doc"])
    print(json.dumps(norm, indent=2))

    # print("\n--- Milvus search results ---")
    # for qi, hits in enumerate(results):
    #     print(f"\nQuery: {queries[qi]}")
    #     for rank, hit in enumerate(hits, start=1):
    #         # fields available: id, distance, entity (with stored fields)
    #         text = hit.get("entity", {}).get("doc")
    #         print(f"  {rank}. id={hit.get('id')}  score={hit.get('distance'):.4f}  doc={text}")

    # # Cosine sanity check using the same embedder
    # embedder = db.embedder
    # q_vecs = concat_chunks(embedder.encode(queries, is_query=True, batch_size=8))
    # d_vecs = concat_chunks(embedder.encode(docs,    is_query=False, batch_size=8))
    # sims = q_vecs @ d_vecs.T  # L2-normalized → dot = cosine
    # print("\n--- Cosine similarity matrix (queries x docs) ---")
    # np.set_printoptions(precision=3, suppress=True)
    # print(sims)