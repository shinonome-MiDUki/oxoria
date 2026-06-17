from __future__ import annotations
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from pathlib import Path

import numpy as np
import faiss
from tokenizers import Tokenizer
import onnxruntime
import huggingface_hub

from oxoria.global_var import GBVar

class UseVector:
    def __init__(self):
        self.data_dir = GBVar.DATA_DIR

    def drop_model_and_tokenizer(self) -> None:
        if hasattr(self, "onnx_session") and hasattr(self, "tokenizer"):
            return
        model_dir = Path(self.data_dir).resolve().parent / "model"
        model_config_path = model_dir / "config.json"
        if model_dir.exists() and model_config_path.exists():
            return
        model_dir.mkdir(parents=True, exist_ok=True)
        huggingface_hub.snapshot_download(
            repo_id="shinonome-MiDUki/paraphrase-multilingual-MiniLM-based-quantumized-model-forOXORIA",
            local_dir=model_dir
        )
        tokenizer_json_path = model_dir / "tokenizer.json"
        self.tokenizer = Tokenizer.from_file(str(tokenizer_json_path))
        self.tokenizer.enable_padding(direction="right", pad_id=0, pad_token="[PAD]")
        self.tokenizer.enable_truncation(max_length=512)
        onnx_model_path = model_dir / "model_quantized.onnx"
        session_options = onnxruntime.SessionOptions()
        self.onnx_session = onnxruntime.InferenceSession(
            str(onnx_model_path),
            sess_options=session_options,
            providers=["CPUExecutionProvider"]
            )

    def setup_model_and_tokenizer(self) -> None:
        if hasattr(self, "onnx_session") and hasattr(self, "tokenizer"):
            return
        model_dir = Path(self.data_dir).resolve().parent / "model"
        model_config_path = model_dir / "config.json"
        if not model_dir.exists() or not model_config_path.exists():
            self.drop_model_and_tokenizer()
            return
        tokenizer_json_path = model_dir / "tokenizer.json"
        self.tokenizer = Tokenizer.from_file(str(tokenizer_json_path))
        self.tokenizer.enable_padding(direction="right", pad_id=0, pad_token="[PAD]")
        self.tokenizer.enable_truncation(max_length=512)
        onnx_model_path = model_dir / "model_quantized.onnx"
        session_options = onnxruntime.SessionOptions()
        self.onnx_session = onnxruntime.InferenceSession(
            str(onnx_model_path),
            sess_options=session_options,
            providers=["CPUExecutionProvider"]
            )
    
    def create_normalized_embedding_np(self, 
                            input_texts: list[str]
                            ) -> np.ndarray:
        self.setup_model_and_tokenizer()
        encoded_batch = self.tokenizer.encode_batch(input_texts)
        input_ids = np.array([x.ids for x in encoded_batch], dtype=np.int64)
        atten_mask = np.array([x.attention_mask for x in encoded_batch])
        input_feed = {
            "input_ids" : input_ids,
            "attention_mask" : atten_mask
        }
        if "token_type_ids" in [y.name for y in self.onnx_session.get_inputs()]:
            token_type_ids = np.array([x.type_ids for x in encoded_batch], dtype=np.int64)
            input_feed["token_type_ids"] = token_type_ids
        outputs = self.onnx_session.run(None, input_feed=input_feed)
        hidden_state = outputs[0]
        input_mask_expanded = np.expand_dims(atten_mask, axis=-1).astype(np.float32)
        sum_embeddings = np.sum(hidden_state * input_mask_expanded, axis=1)
        sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        embeddings_np = (sum_embeddings / sum_mask).astype(np.float32)
        normalized_embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
        return normalized_embeddings_np

    def search_vector(self, 
                      query_text: list[str], 
                      base_index: faiss.Index, 
                      k: int = 5
                      ) -> tuple[np.ndarray, np.ndarray]:
        normalized_query_embeddings_np = self.create_normalized_embedding_np(query_text)
        if k == -1:
            k = base_index.ntotal
        D_l2, I_l2 = base_index.search(normalized_query_embeddings_np, k)

        return D_l2, I_l2
    
    def get_search_results(self, 
                           query_text: list[str], 
                           base_index: faiss.Index, 
                           search_base: list[str],
                           k: int = 5
                           ) -> list[str]:
        I_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=k)[1]
        search_results = []
        for i in range(k):
            search_results.append(search_base[I_l2[0][i].item()])
        return search_results
    
    def get_distance_result(self,
                            query_text: list[str], 
                            base_index: faiss.Index, 
                            k: int | None = 5
                            ) -> list[float]:
        D_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=k)[0]
        search_distance_results = []
        for i in range(k):
            search_distance_results.append(D_l2[0][i])
            
        return search_distance_results
    
    def get_search_results_by_distance(self, 
                                   query_text: list[str], 
                                   base_index: faiss.Index, 
                                   search_base: list[str],
                                   cutoff: float = 0.6,
                                   max_output: int = 5
                                   ) -> list[tuple[str, float]]:
        D_l2, I_l2 = self.search_vector(query_text=query_text,
                                  base_index=base_index,
                                  k=-1)
        search_results_with_distance = []
        counter = 0
        for i in range(len(I_l2[0])):
            if D_l2[0][i] <= cutoff:
                search_results_with_distance.append(search_base[I_l2[0][i].item()])
                counter += 1
                if counter >= max_output:
                    break
        return search_results_with_distance